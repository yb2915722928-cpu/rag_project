param([string]$ExperimentDir = $PSScriptRoot)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.StorageFile,Windows.Storage,ContentType=WindowsRuntime]
$null = [Windows.Storage.Streams.IRandomAccessStream,Windows.Storage.Streams,ContentType=WindowsRuntime]
$null = [Windows.Storage.Streams.InMemoryRandomAccessStream,Windows.Storage.Streams,ContentType=WindowsRuntime]
$null = [Windows.Storage.Streams.DataWriter,Windows.Storage.Streams,ContentType=WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
$null = [Windows.Graphics.Imaging.SoftwareBitmap,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
$null = [Windows.Media.Ocr.OcrEngine,Windows.Foundation,ContentType=WindowsRuntime]
$null = [Windows.Media.Ocr.OcrResult,Windows.Foundation,ContentType=WindowsRuntime]
$null = [Windows.Globalization.Language,Windows.Globalization,ContentType=WindowsRuntime]
$script:AsTaskMethod = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 -and
    $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
} | Select-Object -First 1
function Wait-WinRtResult($Operation, [Type]$ResultType) {
    $task = $script:AsTaskMethod.MakeGenericMethod($ResultType).Invoke($null, @($Operation))
    if (-not $task.Wait(30000)) { throw 'Windows API operation exceeded 30 seconds' }
    return $task.Result
}
$languages = @([Windows.Media.Ocr.OcrEngine]::AvailableRecognizerLanguages | ForEach-Object { $_.LanguageTag })
if ($languages -contains 'zh-Hans-CN') { $languageTag = 'zh-Hans-CN' }
elseif ($languages.Count -gt 0) { $languageTag = $languages[0] }
else { throw 'No locally available Windows OCR recognizer language' }
$language = [Windows.Globalization.Language]::new($languageTag)
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($language)
if ($null -eq $engine) { throw 'Unable to create local OCR engine' }
$results = @()
foreach ($scale in @(1, 2)) {
    $path = Join-Path $ExperimentDir ("scan-{0}x.png" -f $scale)
    $stream = $null
    $bitmap = $null
    $ocrStage = 'read-image-bytes'
    try {
        # Read the same PNG bytes through normal filesystem access. The sandbox
        # denies StorageFile.GetFileFromPathAsync even for workspace inputs.
        $imageBytes = [System.IO.File]::ReadAllBytes($path)
        $stream = [Windows.Storage.Streams.InMemoryRandomAccessStream]::new()
        $writer = [Windows.Storage.Streams.DataWriter]::new($stream)
        try {
            $writer.WriteBytes($imageBytes)
            $null = Wait-WinRtResult ($writer.StoreAsync()) ([uint32])
            $null = $writer.DetachStream()
        }
        finally { $writer.Dispose() }
        $stream.Seek(0)
        $ocrStage = 'create-decoder'
        $decoder = Wait-WinRtResult ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
        $ocrStage = 'decode-bitmap'
        $bitmap = Wait-WinRtResult ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
        $ocrStage = 'recognize'
        $ocr = Wait-WinRtResult ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
        $lines = @($ocr.Lines | ForEach-Object {
            $line = $_
            $words = @($line.Words | ForEach-Object {
                [ordered]@{text=$_.Text; bounds=[ordered]@{x=$_.BoundingRect.X; y=$_.BoundingRect.Y; width=$_.BoundingRect.Width; height=$_.BoundingRect.Height}}
            })
            [ordered]@{text=$line.Text; words=$words}
        })
        $results += [ordered]@{input=$path; render_scale=$scale; status='recognized'; text=$ocr.Text;
            text_angle=$ocr.TextAngle; width=$bitmap.PixelWidth; height=$bitmap.PixelHeight;
            coordinate_space='pixels in this OCR input image'; lines=$lines}
    }
    catch { $results += [ordered]@{input=$path; render_scale=$scale; status='failed'; stage=$ocrStage; error=$_.Exception.ToString()} }
    finally {
        if ($null -ne $bitmap) { $bitmap.Dispose() }
        if ($null -ne $stream) { $stream.Dispose() }
    }
}
$report = [ordered]@{environment=[ordered]@{engine='Windows.Media.Ocr.OcrEngine';
    os=[Environment]::OSVersion.VersionString; powershell=$PSVersionTable.PSVersion.ToString();
    available_languages=$languages; selected_language=$languageTag;
    max_image_dimension=[Windows.Media.Ocr.OcrEngine]::MaxImageDimension}; results=$results}
$json = $report | ConvertTo-Json -Depth 15
[System.IO.File]::WriteAllText((Join-Path $ExperimentDir 'raw-ocr.json'), $json, [System.Text.UTF8Encoding]::new($false))
$results | ForEach-Object { [pscustomobject]@{Scale=$_.render_scale; Status=$_.status; Text=$_.text; Error=$_.error} }
