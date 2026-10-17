# MaxKB source excerpt: installer/start-maxkb.sh

- source: https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/installer/start-maxkb.sh
- raw: https://raw.githubusercontent.com/1Panel-dev/MaxKB/0fa9a0dae8850c1878f087f0d81c974c1d424b06/installer/start-maxkb.sh
- publisher: 1Panel-dev/MaxKB
- pub_date: 未标
- accessed: 2026-10-15
- confidence: medium（单一官方源）
- class: official-pinned-source

```text
1: #!/bin/bash
2: 
3: if [ ! -d /opt/maxkb/logs ]; then
4:     mkdir -p /opt/maxkb/logs
5: fi
6: chmod -R 700 /opt/maxkb/logs
7: if [ ! -d /opt/maxkb/local ]; then
8:     mkdir -p /opt/maxkb/local
9:     chmod 700 /opt/maxkb/local
10: fi
11: mkdir -p /opt/maxkb/python-packages
...
26: python /opt/maxkb-app/main.py start
```
