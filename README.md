### Notion_MCP 

> 현재 프로젝트는 커스텀으로 만든  notion 특정 db 접근 mcp server로 되어있습니다


### notion api mcp server

#### 사용법

> config.json 수정
```json

{
  "custonNotion": {
    "command": "python",
    "args": [
      "./mcp_server_notion.py"
    ],
    "transport": "stdio"
  }
}

```

> env. 
```json
ANTHROPIC_API_KEY= # llm api key 필요
OPENAI_API_KEY= # llm api key 필요


DB=  # 노션 db 링크
NOTION_API_KEY= # 노션 api 링크
```




#### 공식 notion mcp 사용법
- https://developers.notion.com/docs/mcp
> npx -y @notionhq/notion-mcp-server

> config.json 수정
```json
{
  "mcpServers": {
    "notionApi": {
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": {
        "OPENAPI_MCP_HEADERS": "{\"Authorization\": \"Bearer ntn_****\", \"Notion-Version\": \"2022-06-28\" }"  # 노션 api키 필요 
      }
    }
  }
}
```



> env. 
```json
ANTHROPIC_API_KEY= # llm api key 필요
OPENAI_API_KEY= # llm api key 필요
```




