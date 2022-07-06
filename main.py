from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sentencepiece as spm

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://100knock-translation.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 環境変数設定
os.environ["MKL_THREADING_LAYER"] = "GNU"

# ローカル環境時のモデルURL
url = "../nlp100-2022/hattori/chapter10"

# sentencepieceのロード
spja = spm.SentencePieceProcessor()
spja.Load(f"{url}/sentencepiece/ja.model")

@app.get("/api/hoge")
def Hello():
    return {"初期テキストをAPIから取得しました！"}

@app.post("/api/translation/{text}")
def Translate(text: str):
    text = text.replace(",", "、").replace("，", "、").replace(".", "。").replace("．", "。").replace(" ", "").replace("　","").replace("(", "").replace(")", "")
    ja = " ".join(spja.EncodeAsPieces(text))
    stream = os.popen(f"echo {ja} | CUDA_VISIBLE_DEVICES=1 fairseq-interactive {url}/data-bin-domains \
                        --input - \
                        --path {url}/checkpoints-domains/checkpoint_best.pt \
                        --beam 32 \
                        --buffer-size 1024 \
                        --batch-size 256 \
                        | grep '^H' \
                        | cut -f3 ")
    en = stream.read()
    ja_decoding = ja.replace(" ", "").replace("▁", " ").strip()
    en_decoding = en.replace(" ", "").replace("▁", " ").strip()
    return {"ja": ja_decoding, "en": en_decoding}
