import uvicorn
import argparse

def main():
    parser = argparse.ArgumentParser(description="启动FastAPI服务器")
    parser.add_argument("--host", default="0.0.0.0", help="绑定的主机地址")
    parser.add_argument("--port", default=8001, type=int, help="绑定的端口")
    args = parser.parse_args()
    
    print(f"正在启动服务器，访问地址: http://{args.host}:{args.port}")
    uvicorn.run("app.main:app", host=args.host, port=args.port, reload=True)

if __name__ == "__main__":
    main() 