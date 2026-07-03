
from pymilvus import connections, FieldSchema, DataType, CollectionSchema, Collection
from pymilvus.orm import utility

from app.config import settings


#新建milvus连接
#连接milvus，并获取简历向量集合，没有集合就自动创建
#我要连接 Milvus 数据库、连接地址是 settings.MILVUS_HOST、端口是 settings.MILVUS_PORT、连接别名叫 default
def get_collection()-> Collection:
    connections.connect(
        alias="default",
        host=settings.MILVUS_HOST,
        port=str(settings.MILVUS_PORT)
    )
    #获取集合名称
    collection_name=settings.MILVUS_COLLECTION_NAME
    #看一下这个集合是否存在
    if not utility.has_collection(collection_name):
        #定义milvus表的结构，就像mysql表结构一样
        fields=[
            FieldSchema(name="id",dtype=DataType.INT64,is_primary=True,auto_id=True),
            FieldSchema(name="resume_id",dtype=DataType.INT64),
            FieldSchema(name="embedding",dtype=DataType.FLOAT_VECTOR,dim=1536)
        ]
        #用刚才定义的字段创建一个集合结构，相当于创建mysql的表
        schema=CollectionSchema(fields=fields,description="resume embedding collection")
        collection=Collection(name=collection_name,schema=schema)
        #给embedding字段创建索引
        index_params={
            "index_type":"IVF_FLAT",
            #相似度计算方式是余弦相似度
            "metric_type":"COSINE",
            #索引分桶数量？
            "params":{"nlist":128}
        }
        collection.create_index(field_name="embedding",index_params=index_params)
        #把集合加载到内存中
        collection.load()
        #返回创建的milvus集合对象
        return collection

    collection=Collection(name=collection_name)
    collection.load()
    return collection

#把某个简历的向量embedding插入到milvus里面，并返回milvus自动生成的主键ID
def insert_resume_embedding(resume_id:int,embedding:list[float]) ->int:
    collection=get_collection()

    data=[
        [resume_id],
        [embedding]
    ]

    result=collection.insert(data)
    collection.flush()
    #返回的主键id
    return result.primary_keys[0]

#向量检索
def search_resume_embeddings(query_vector:list[float],top_k:int):
    #获取连接
    collection=get_collection()
    results=collection.search(
        data=[query_vector],
        anns_field="embedding", #用集合里的embedding字段做向量检索
        param={
            "metric_type":"COSINE", #向量检索方式相似度搜索
            "params":{"nprobe":10}
        },
        limit=top_k,
        output_fields=["resume_id"] #命中的简历
    )

    return results[0] if results else []

#根据简历id取向量
def get_resume_embedding_by_resume_id(resume_id:int):
    collection=get_collection()
    results=collection.query(
        expr=f"resume_id=={resume_id}",
        output_fields=["resume_id","embedding"]
    )
    if not results:
        return None
    return results[0]


def delete_resume_embedding_by_resume_id(resume_id: int):
    collection = get_collection()
    collection.delete(expr=f"resume_id == {resume_id}")
    collection.flush()
