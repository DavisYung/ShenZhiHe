# -*- coding: utf-8 -*-
"""生成 extras/math/programs.json（fx-50FH II 四段程式碼）。"""
import io, json, os

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
OUT = os.path.join(ROOT, "extras", "math", "programs.json")

P1 = """?→A:?→B:?→C:?→D:?→X:?→Y:
(A+C+X)÷3◢
(B+D+Y)÷3◢
A−X→A:B−Y→B:C−X→C:D−Y→D:
√(C²+D²)+√(A²+B²)+√((A−C)²+(B−D)²)→M:
(√(C²+D²)A+√(A²+B²)C)÷M+X◢
(√(C²+D²)B+√(A²+B²)D)÷M+Y◢
2(AD−CB)→M:
((A²+B²)D−(C²+D²)B)÷M+X◢
((C²+D²)A−(A²+B²)C)÷M+Y◢
A+C+X−2((A²+B²)D−(C²+D²)B)÷M◢
B+D+Y−2((C²+D²)A−(A²+B²)C)÷M◢"""

P2 = """?→A:?→B:?→C:?→D:?→X:?→Y:
AX−BD→M:
(CX−BY)÷M→B:
(AY−CD)÷M→A:
?→C:?→D:?→X:
B◢A◢CB+DA+X◢"""

P3 = """Fix 4:?→A:?→B:?→C:?→D:?→X:
Lbl 1:
Asin(X)²+Bcos(X)²+Csin(X)+Dcos(X)→Y:
Abs(Y)<1E-9⇒Goto 2:
X+1E-4→M:
Asin(M)²+Bcos(M)²+Csin(M)+Dcos(M)→M:
X−Y×1E-4÷(M−Y)→X:
X◢:
Goto 1:
Lbl 2:X◢"""

P4 = """?→A:?→B:?→C:
C<0⇒√(A²+B²−2ABcos(C))→C:
(A+B+C)÷2→X:
√(X(X−A)(X−B)(X−C))◢
cos⁻¹((B²+C²−A²)÷(2BC))→D:D◢
cos⁻¹((C²+A²−B²)÷(2CA))→M:M◢
180−D−M◢
A÷sin(D)÷2→M:M◢
?→D:2M sin(D)◢"""

data = {
    "id": "programs",
    "type": "code",
    "order": 1,
    "emoji": "🖩",
    "title": "fx-50FH II 四段萬能程式碼",
    "subtitle": "照抄即可重建。四段程式分別佔 P1～P4，總佔約 621／680 字節。",
    "source": "CASIO fx-50FH II（H.K.E.A.A. APPROVED 港版，7 個變數 A B C D X Y M）實機驗收",
    "note": "調用方式：按 Prog 再按區號（例：Prog 2 EXE）。全部程式需 DEG 模式；P3 跑完要按 SHIFT → MODE → 6 → 0 關掉 Fix。",
    "groups": [
        {
            "id": "p1",
            "area": "P1",
            "title": "三點求四心",
            "desc": "輸入三個頂點座標，輸出形心、內心、外心、垂心，嚴格成對（Gx,Gy → Ix,Iy → Ox,Oy → Hx,Hy）。",
            "bytes": "約 271",
            "code": P1,
            "io": [
                {"k": "輸入", "v": "A,B＝點1　C,D＝點2　X,Y＝點3"},
                {"k": "輸出", "v": "1 Gx｜2 Gy｜3 Ix｜4 Iy｜5 Ox｜6 Oy｜7 Hx｜8 Hy"}
            ],
            "verify": "輸入 (0,0)、(4,0)、(0,3) → 1.3333 / 1 / 1 / 1 / 2 / 1.5 / 0 / 0",
            "pitfalls": [
                "第 4 行 A−X→A:B−Y→B:C−X→C:D−Y→D 四個 → 一個都不能漏，這是「平移讓第三點成原點」的省字節核心。",
                "第 5 行結尾是 →M:（冒號），不是 ◢，這裡只存周長不輸出。",
                "三點共線時外心分母為 0，報 Math ERROR 屬正常。"
            ]
        },
        {
            "id": "p2",
            "area": "P2",
            "title": "線性規劃（兼解二元一次方程組）",
            "desc": "輸入兩條線的係數求交點，再輸入目標函數係數直接輸出目標值。三條不等式就分三次跑，每次取一對線。",
            "bytes": "80（實測）",
            "code": P2,
            "io": [
                {"k": "輸入", "v": "A,B,C＝線1（Ax+By=C）　D,X,Y＝線2（Dx+Xy=Y）　再輸 p,q,r"},
                {"k": "輸出", "v": "1 交點x｜2 交點y｜3 目標值 px+qy+r"}
            ],
            "verify": "2x+3y=7、x−y=1（第三組輸 0 0 0）→ 2 / 1 / 0",
            "pitfalls": [
                "解二元一次方程組：第三組輸 0 0 0，前兩個輸出就是解；或出 y 之後直接按 AC。",
                "缺項要補 0：x=3 寫成 1,0,3；y=5 寫成 0,1,5。",
                "線性規劃每個交點都要代回「沒參與的那條不等式」檢驗，不過關的才是陷阱答案。"
            ]
        },
        {
            "id": "p3",
            "area": "P3",
            "title": "三角方程萬能求根",
            "desc": "內建通式 f(X)=A·sin²X+B·cos²X+C·sinX+D·cosX，用割線法迭代求根。換題只輸 A B C D，程式永不改。",
            "bytes": "約 124",
            "code": P3,
            "io": [
                {"k": "輸入", "v": "A,B,C,D＝四個係數　X＝初值"},
                {"k": "輸出", "v": "收斂到的根（一個）"}
            ],
            "verify": "A=−2,B=0,C=−1,D=0、初值 135 → 180",
            "pitfalls": [
                "一次只收斂到最近的一個根，要換初值掃。萬能四初值：45 / 135 / 225 / 315。",
                "初值別用 90°、270°（導數為 0，會跑出天文數字）。",
                "跑完一定要 SHIFT → MODE → 6 → 0 關掉 Fix，否則後續計算全被截成 4 位。",
                "含 sinθ·cosθ 交叉項要先因式分解成兩段，通式表達不了。"
            ]
        },
        {
            "id": "p4",
            "area": "P4",
            "title": "正弦餘弦希羅三合一",
            "desc": "輸入三邊（或兩邊一夾角，第三個數用負數）一次輸出：面積、三個角、外接圓半徑，最後還能輸入任意角反推對邊。",
            "bytes": "約 146",
            "code": P4,
            "io": [
                {"k": "輸入", "v": "A,B,C＝三邊；已知兩邊一夾角時，第三個數輸負數代表夾角"},
                {"k": "輸出", "v": "1 面積｜2 ∠A｜3 ∠B｜4 ∠C｜5 外接圓半徑 R｜6 輸入角→對邊"}
            ],
            "verify": "輸入 3、4、5 → 6 / 36.87 / 53.13 / 90 / 2.5",
            "pitfalls": [
                "第三個輸入為負＝夾角模式（cos(−θ)=cosθ，負號只當開關）。",
                "夾角題的第 4 個輸出應等於你輸入的夾角，可當輸入正確性自檢。",
                "三個角相加必須等於 180°；大邊對大角。",
                "不滿足三角形不等式會報 Math ERROR，屬正常。"
            ]
        }
    ],
    "quick": "P1 四心　三座標 → G I O H（8 數成對）\nP2 線性　兩線 + pqr → x y 目標（方程組：第三組 0 0 0）\nP3 求根　A B C D → 根（初值 45/135/225/315）\nP4 三角　三邊 → 面積/三角/R（兩邊+夾角：第三數用負）\n\n全體：DEG 模式；P3 跑完 SHIFT MODE 6 0 關 Fix",
    "bytes_table": [
        {"area": "P1", "what": "三點求四心", "bytes": "約 271"},
        {"area": "P2", "what": "線性規劃 + 方程組", "bytes": "80"},
        {"area": "P3", "what": "三角方程求根", "bytes": "約 124"},
        {"area": "P4", "what": "正弦餘弦希羅三合一", "bytes": "約 146"},
        {"area": "剩餘", "what": "680 − 621", "bytes": "約 59"}
    ]
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write("\n")

# 驗證：重新讀回，確認可解析且程式碼未變形
with io.open(OUT, encoding="utf-8") as f:
    back = json.load(f)
assert [g["code"] for g in back["groups"]] == [P1, P2, P3, P4], "程式碼在序列化過程被改動"
assert "\ufffd" not in json.dumps(back, ensure_ascii=False), "出現亂碼 U+FFFD"
print("OK -> %s" % OUT)
print("groups=%d  size=%d bytes" % (len(back["groups"]), os.path.getsize(OUT)))
