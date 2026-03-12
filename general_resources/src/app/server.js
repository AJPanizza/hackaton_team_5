const http = require("http");

const server = http.createServer((req, res) => {
  if (req.url === "/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ status: "ok" }));
  } else {
    res.writeHead(200, { "Content-Type": "text/html" });
    res.end("<h1>Hello from Team Five!</h1><p>CGM NBA Pipeline — running on Node.js.</p>");
  }
});

server.listen(8080, "0.0.0.0", () => {
  console.log("Server running on port 8080");
});
