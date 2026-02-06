const http = require("http");

const server = http.createServer((req, res) => {
  // CORS 설정 (프론트와 포트가 다를 경우 대비)
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS');

  if (req.method === "POST" && req.url === "/api/upload") {
    // 실제 구현 시에는 'multer' 같은 라이브러리를 써서 binary 데이터를 파싱해야 합니다.
    console.log("이미지 수신 요청 감지");
    
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({
      message: "서버에 데이터가 도달했습니다. (현재는 Mock 데이터 응답)",
      status: "received"
    }));
  } else {
    res.writeHead(200, { "Content-Type": "text/plain" });
    res.end("AI Backend Server Prototype is running on port 3000");
  }
});

server.listen(3000, () => {
  console.log("서버가 http://localhost:3000 에서 실행 중입니다.");
});