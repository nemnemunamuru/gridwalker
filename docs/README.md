# Documentation

このフォルダにはプロジェクトのドキュメントを置きます。

- 開発手順
- API仕様
- 使用方法

環境セットアップメモ

1. 依存定義はプロジェクトルートの `pyproject.toml` にあります（Python `>=3.13`）。
2. 同等のロックファイルとして `uv.lock` を用意しました。

注意: 今回リポジトリ上で `.venv` にパッケージをインストールしようとしましたが、ネットワーク経由で PyPI に接続する際に SSL 証明書検証エラーが発生し、インストールが失敗しました。

ローカルで依存をインストールする手順（PowerShell）:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install "matplotlib>=3.10.9" "numpy>=2.4.4" "pandas>=3.0.2"
```

もし SSL エラーが出る場合は、社内プロキシや CA 証明書の設定を確認するか、信頼できるネットワークで再実行してください。

