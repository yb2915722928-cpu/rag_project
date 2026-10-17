# Source: https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/vector/pg_vector.py
# retrieved: 2026-10-15; first_source_line: 145

                        all_results.extend(results)
                    all_results.sort(key=lambda x: x.get("similarity", x.get("comprehensive_score", 0)), reverse=True)
                    return all_results[:top_number]

    def query(
        self,
        query_text: str,
        query_embedding: List[float],
        knowledge_id_list: list[str],
        document_id_list: list[str],
        exclude_document_id_list: list[str],
        exclude_paragraph_list: list[str],
        is_active: bool,
        top_n: int,
        similarity: float,
        search_mode: SearchMode,
    ):
        exclude_dict = {}
        if knowledge_id_list is None or len(knowledge_id_list) == 0:
            return []
        for search_handle in search_handle_list:
            if search_handle.support(search_mode):
                # Query per knowledge base to leverage per-KB partial HNSW indexes
                # (WHERE knowledge_id = '{k_id}'), which won't be used with knowledge_id__in
                def build_query_set(kid):
                    qs = QuerySet(Embedding).filter(knowledge_id=kid, is_active=is_active)
                    if document_id_list is not None and len(document_id_list) > 0:
                        qs = qs.filter(document_id__in=document_id_list)
                    if exclude_document_id_list is not None and len(exclude_document_id_list) > 0:
                        qs = qs.exclude(document_id__in=exclude_document_id_list)
                    if exclude_paragraph_list is not None and len(exclude_paragraph_list) > 0:
                        qs = qs.exclude(paragraph_id__in=exclude_paragraph_list)
                    qs = qs.exclude(**exclude_dict)
                    return qs
                if len(knowledge_id_list) == 1:
                    query_set = build_query_set(knowledge_id_list[0])
                    return search_handle.handle(
                        query_set, query_text, query_embedding, top_n, similarity, search_mode, knowledge_id_list
                    )
                else:
                    all_results = []
                    for kid in knowledge_id_list:
                        query_set = build_query_set(kid)
                        results = search_handle.handle(
                            query_set, query_text, query_embedding, top_n, similarity, search_mode, knowledge_id_list
                        )
                        all_results.extend(results)
                    all_results.sort(key=lambda x: x.get("similarity", x.get("comprehensive_score", 0)), reverse=True)
                    return all_results[:top_n]

    def update_by_source_id(self, source_id: str, instance: Dict):
        QuerySet(Embedding).filter(source_id=source_id).update(**instance)

    def update_by_paragraph_id(self, paragraph_id: str, instance: Dict):
        QuerySet(Embedding).filter(paragraph_id=paragraph_id).update(**instance)

    def update_by_paragraph_ids(self, paragraph_id: str, instance: Dict):
        QuerySet(Embedding).filter(paragraph_id__in=paragraph_id).update(**instance)

    def delete_by_knowledge_id(self, knowledge_id: str):
        QuerySet(Embedding).filter(knowledge_id=knowledge_id).delete()

    def delete_by_knowledge_id_list(self, knowledge_id_list: List[str]):
        QuerySet(Embedding).filter(knowledge_id__in=knowledge_id_list).delete()

    def delete_by_document_id(self, document_id: str):
        QuerySet(Embedding).filter(document_id=document_id).delete()
        return True

    def delete_by_document_id_list(self, document_id_list: List[str]):
        if len(document_id_list) == 0:
            return True
        return QuerySet(Embedding).filter(document_id__in=document_id_list).delete()

    def delete_by_source_id(self, source_id: str, source_type: str):
        QuerySet(Embedding).filter(source_id=source_id, source_type=source_type).delete()
        return True

    def delete_by_paragraph_id(self, paragraph_id: str):
        QuerySet(Embedding).filter(paragraph_id=paragraph_id).delete()

    def delete_by_paragraph_ids(self, paragraph_ids: List[str]):
        QuerySet(Embedding).filter(paragraph_id__in=paragraph_ids).delete()


class ISearch(ABC):
    @abstractmethod
    def support(self, search_mode: SearchMode):
        pass

    @abstractmethod
    def handle(
        self,
        query_set,
        query_text,
        query_embedding,
        top_number: int,
        similarity: float,
        search_mode: SearchMode,
        knowledge_id_list: list[str] = None,
    ):
        pass


class EmbeddingSearch(ISearch):
    def handle(
        self,
        query_set,
        query_text,
        query_embedding,
        top_number: int,
        similarity: float,
        search_mode: SearchMode,
        knowledge_id_list: list[str] = None,
    ):
        exec_sql, exec_params = generate_sql_by_query_dict(
            {"embedding_query": query_set},
            select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "knowledge", "sql", "embedding_search.sql")
            ),
            with_table_name=True,
        )
        embedding_model = select_list(
            exec_sql, [len(query_embedding), json.dumps(query_embedding), *exec_params, len(query_embedding), json.dumps(query_embedding), top_number, similarity, top_number]
        )
        return embedding_model

    def support(self, search_mode: SearchMode):
        return search_mode.value == SearchMode.embedding.value


class KeywordsSearch(ISearch):
    def handle(
        self,
        query_set,
        query_text,
