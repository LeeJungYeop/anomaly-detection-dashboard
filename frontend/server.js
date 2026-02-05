const http = require("http");

http.createServer((req, res) => {
  res.end("hello frontend");
}).listen(3000);
