import io,sys
sys.stdout.reconfigure(encoding="utf-8")
p="site/template.html"
with io.open(p,encoding="utf-8") as f: lines=f.readlines()
# 删除第 270~306 行（1-based），即索引 269..305
start=269; end=306  # 不含 306
print("删除首行:",repr(lines[start][:60]))
print("删除末行:",repr(lines[end-1][:60]))
print("保留下一行:",repr(lines[end][:60]))
new=lines[:start]+lines[end:]
with io.open(p,"w",encoding="utf-8",newline="\n") as f: f.writelines(new)
print("完成，原行数",len(lines),"新行数",len(new))
