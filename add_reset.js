const fs = require('fs');
const html = fs.readFileSync('C:/Users/29763/github-family-tree/index.html', 'utf8');

const titleTag = '<title>朱氏三厢房家族族谱</title>';
const resetScript = titleTag + `
<script>if(location.search.includes("reset=1")){localStorage.clear();document.title="已清除";document.body.innerHTML="<div style=text-align:center;padding:60px 20px;font-size:18px>已清除缓存!<br><br><a href="+location.pathname+" style=color:#b8860b>点击重新打开</a></div>";}</script>`;

const fixed = html.replace(titleTag, resetScript);
fs.writeFileSync('C:/Users/29763/github-family-tree/index.html', fixed);
console.log('Added reset mechanism');
