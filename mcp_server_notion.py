from dotenv import load_dotenv
import os
from notion_client import Client
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

# --- 환경 변수 로드 ---
load_dotenv()

# --- Notion API 설정 ---
NOTION_TOKEN = os.getenv("NOTION_API_KEY")
DEFAULT_DATABASE_ID = os.getenv("DB", "")  

# --- Pydantic 모델 정의 ---
class NotionQueryParameters(BaseModel):
    """
    Notion 데이터베이스를 쿼리할 때 필요한 매개변수입니다.
    """
    database_id: Optional[str] = Field(
        DEFAULT_DATABASE_ID,
        description="조회할 Notion 데이터베이스의 ID"
    )
    filter_conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="필터 조건 (예: {\"property\": \"상태\", \"select\": {\"equals\": \"진행 중\"}})"
    )
    sort_conditions: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="정렬 조건 (예: [{\"property\": \"생성일\", \"direction\": \"descending\"}])"
    )
    page_size: int = Field(
        100,
        description="가져올 항목 최대 개수 (1~100)"
    )

# --- FastMCP 서버 초기화 ---
mcp = FastMCP(
    "Notion",
    instructions="너는 Notion API를 호출하여 데이터베이스에서 정보를 조회하는 도구야.",
    host="0.0.0.0",
    port=8000,
)

# --- Notion 데이터베이스 쿼리 툴 함수 ---
@mcp.tool(description="""
    Notion 데이터베이스에서 항목을 조회합니다.
    filter_conditions와 sort_conditions는 Notion API 쿼리 형식을 따라야 합니다.
""")
async def notionSelect(params: NotionQueryParameters):
    if not NOTION_TOKEN:
        return {"error": "❌ Notion API 토큰이 설정되지 않았습니다."}

    if not params.database_id:
        return {"error": "❌ 데이터베이스 ID가 제공되지 않았습니다."}

    notion_client = Client(auth=NOTION_TOKEN)
    items = []
    has_more = True
    start_cursor = None

    print(f"[INFO] Notion 데이터베이스 '{params.database_id}'에서 항목 조회 중...")
    print(f"필터 조건: {params.filter_conditions}")
    print(f"정렬 조건: {params.sort_conditions}")

    try:
        while has_more and len(items) < params.page_size:
            query_kwargs = {
                "database_id": params.database_id,
                "page_size": min(100, params.page_size - len(items)),
            }
            if start_cursor:
                query_kwargs["start_cursor"] = start_cursor
            if params.filter_conditions:
                query_kwargs["filter"] = params.filter_conditions
            if params.sort_conditions:
                query_kwargs["sorts"] = params.sort_conditions

            response = notion_client.databases.query(**query_kwargs)
            items.extend(response["results"])
            has_more = response.get("has_more", False)
            start_cursor = response.get("next_cursor")

            if not has_more or start_cursor is None:
                break

    except Exception as e:
        print(f"[ERROR] Notion API 호출 중 오류 발생: {e}")
        return {"error": f"Notion API 호출 오류: {e}"}

    # 결과 정리: 각 항목의 속성을 간단히 파싱
    parsed_items = []
    for item in items:
        properties = {}
        for prop_name, prop_data in item.get("properties", {}).items():
            prop_type = prop_data.get("type")
            if prop_type == "title":
                properties[prop_name] = "".join([t.get("plain_text", "") for t in prop_data.get("title", [])])
            elif prop_type == "rich_text":
                properties[prop_name] = "".join([t.get("plain_text", "") for t in prop_data.get("rich_text", [])])
            elif prop_type == "number":
                properties[prop_name] = prop_data.get("number")
            elif prop_type == "select":
                properties[prop_name] = prop_data.get("select", {}).get("name")
            elif prop_type == "multi_select":
                properties[prop_name] = [s.get("name") for s in prop_data.get("multi_select", [])]
            elif prop_type == "date":
                properties[prop_name] = prop_data.get("date", {}).get("start")
            else:
                properties[prop_name] = prop_data  # 기타 타입은 원본 유지

        parsed_items.append({
            "id": item["id"],
            "url": item.get("url"),
            "created_time": item.get("created_time"),
            "last_edited_time": item.get("last_edited_time"),
            "properties": properties,
        })

    return {
        "status": "success",
        "count": len(parsed_items),
        "data": parsed_items,
    }

# --- 서버 실행 ---
if __name__ == "__main__":
    if not NOTION_TOKEN:
        print("❗ 경고: NOTION_API_KEY 환경 변수가 설정되지 않았습니다.")
    if not DEFAULT_DATABASE_ID:
        print("❗ 경고: NOTION_DATABASE_ID 환경 변수가 설정되지 않았습니다.")

    print("\n✅ FastMCP 서버 시작: http://0.0.0.0:8000")
    print("Notion API 연결을 확인하세요.")
    mcp.run(transport="stdio")
