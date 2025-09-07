from aiohttp import web

routes = web.RouteTableDef()

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Snowball File Store Bot</title>
  <style>
    body {
      margin: 0;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #1e3c72, #2a5298);
      color: #fff;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      overflow: hidden;
    }
    .container {
      text-align: center;
      padding: 2rem;
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(12px);
      border-radius: 20px;
      box-shadow: 0 8px 25px rgba(0,0,0,0.3);
      animation: fadeIn 1.2s ease-in-out;
    }
    h1 {
      font-size: 2.5rem;
      margin-bottom: 0.5rem;
      background: linear-gradient(90deg, #00f2fe, #4facfe);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      animation: slideDown 1s ease-out;
    }
    p {
      font-size: 1.2rem;
      margin: 0.5rem 0 1.5rem;
      color: #e0e0e0;
      animation: fadeInUp 1.5s ease-out;
    }
    a.button {
      display: inline-block;
      padding: 0.75rem 1.5rem;
      font-size: 1rem;
      color: #fff;
      background: linear-gradient(135deg, #00c6ff, #0072ff);
      border-radius: 30px;
      text-decoration: none;
      font-weight: 600;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    a.button:hover {
      transform: translateY(-3px);
      box-shadow: 0 6px 15px rgba(0,0,0,0.25);
    }
    .footer {
      margin-top: 1.5rem;
      font-size: 0.9rem;
      color: #ccc;
      animation: fadeIn 2s ease-in-out;
    }
    @keyframes fadeIn {
      from {opacity: 0;}
      to {opacity: 1;}
    }
    @keyframes fadeInUp {
      from {opacity: 0; transform: translateY(20px);}
      to {opacity: 1; transform: translateY(0);}
    }
    @keyframes slideDown {
      from {opacity: 0; transform: translateY(-20px);}
      to {opacity: 1; transform: translateY(0);}
    }
    .wave {
      position: absolute;
      bottom: 0;
      width: 200%;
      height: 200px;
      background: rgba(255,255,255,0.1);
      border-radius: 100%;
      animation: waveAnim 6s infinite linear;
    }
    @keyframes waveAnim {
      from { transform: translateX(0); }
      to { transform: translateX(-50%); }
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>❆ Snowball File Secure Bot ❆</h1>
    <p>Your reliable bot to store and share files permanently with a single link.</p>
    <a href="https://t.me/SnowFileSecureBot" target="_blank" class="button">🚀 Open in Telegram</a>
    <div class="footer">Made with ❤️ by <a href="https://t.me/Snowball_Official" target="_blank" style="color:#4facfe;text-decoration:none;">Snowball</a></div>
  </div>
  <div class="wave"></div>
</body>
</html>
"""

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.Response(text=HTML_PAGE, content_type="text/html")

async def web_server():
    web_app = web.Application(client_max_size=30_000_000)
    web_app.add_routes(routes)
    return web_app
