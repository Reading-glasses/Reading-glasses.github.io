#!/bin/bash

# 收集 HTML 文件（排除 index.html）
mapfile -d '' files < <(find . -type f -name "*.html" ! -name "index.html" -print0)

# 生成首页导航
{
  echo "<!DOCTYPE html>"
  echo "<html><head><meta charset='utf-8'><title>reading glasses</title></head><body>"
  echo "<h1>reading glasses</h1><ul>"
  for file in "${files[@]}"; do
    file="${file#./}"
    name="${file%.html}"                # 去掉 .html 后缀
    display_name=$(echo "$name" | sed 's/-/ /g')  # - 替换为空格
    url=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$file'))")
    echo "<li><a href=\"$url\">$display_name</a></li>"
  done
  echo "</ul></body></html>"
} > index.html

# 给每个 HTML 页面添加随机内部链接
for file in "${files[@]}"; do
  file="${file#./}"

  # 移除已有 internal-links 区块
  sed -i '/<!-- internal-links start -->/,/<!-- internal-links end -->/d' "$file"

  # 构建候选链接（排除自己）
  other_links=()
  for link in "${files[@]}"; do
    link="${link#./}"
    [[ "$link" != "$file" ]] && other_links+=("$link")
  done

  # 打乱顺序
  shuffled=($(shuf -e "${other_links[@]}"))

  # 随机选 3-5 个链接
  count=$(shuf -i 3-5 -n 1)
  selected=("${shuffled[@]:0:$count}")

  # 写入 HTML
  {
    echo "<!-- internal-links start -->"
    echo "<hr><h2>Other Pages</h2><ul>"
    for link in "${selected[@]}"; do
      name="${link%.html}"
      display_name=$(echo "$name" | sed 's/-/ /g')
      url=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$link'))")
      echo "<li><a href=\"$url\">$display_name</a></li>"
    done
    echo "</ul><!-- internal-links end -->"
  } >> "$file"
done
