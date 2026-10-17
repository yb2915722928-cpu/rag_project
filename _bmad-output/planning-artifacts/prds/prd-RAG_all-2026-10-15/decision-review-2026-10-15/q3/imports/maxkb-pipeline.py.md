# Source: https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/chat/serializers/chat.py
# retrieved: 2026-10-15; first_source_line: 335

            raise ChatException(500, _("The current model is not available"))
        if model.status == Status.DOWNLOAD:
            raise ChatException(500, _("The model is downloading, please try again later"))
        return chat_info

    def chat_simple(self, chat_info: ChatInfo, instance, base_to_response):
        message = instance.get('message')
        re_chat = instance.get('re_chat')
        stream = instance.get('stream')
        chat_user_id = self.data.get('chat_user_id')
        chat_user_type = self.data.get('chat_user_type')
        ip_address = self.data.get('ip_address')
        source = self.data.get('source')
        form_data = instance.get("form_data")
        chat_record_id = instance.get('chat_record_id')
        pipeline_manage_builder = PipelineManage.builder()
        # 如果开启了问题优化,则添加上问题优化步骤
        if chat_info.application.problem_optimization:
            pipeline_manage_builder.append_step(BaseResetProblemStep)
        # 构建流水线管理器
        pipeline_message = (pipeline_manage_builder.append_step(BaseSearchDatasetStep)
                            .append_step(BaseGenerateHumanMessageStep)
                            .append_step(BaseChatStep)
                            .add_base_to_response(base_to_response)
                            .add_debug(self.data.get('debug', False))
                            .build())
        exclude_paragraph_id_list = []
        # 相同问题是否需要排除已经查询到的段落
        if re_chat:
            paragraph_id_list = flat_map(
                [[paragraph.get('id') for paragraph in chat_record.details['search_step']['paragraph_list']] for
                 chat_record in chat_info.chat_record_list if
                 chat_record.problem_text == message and 'search_step' in chat_record.details and 'paragraph_list' in
                 chat_record.details['search_step']])
            exclude_paragraph_id_list = list(set(paragraph_id_list))
        # 构建运行参数
        params = chat_info.to_pipeline_manage_params(message, get_post_handler(chat_info), exclude_paragraph_id_list,
                                                     chat_user_id, chat_user_type, ip_address, source, stream,
                                                     form_data)
        if chat_record_id:
            params['chat_record_id'] = chat_record_id
