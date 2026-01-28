$env:OUTGOING_ENDPOINT = 'https://httpbin.org/post'
$env:API_KEY = 'test_server_key'
$env:ADMIN_API_KEY = 'test_admin_key'
& 'D:\Agentic_Honey_Pot\.venv\Scripts\uvicorn.exe' 'backend.app.main:app' --host 127.0.0.1 --port 8030
