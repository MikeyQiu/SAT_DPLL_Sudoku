# NumberPlaceSolver
簡単に言うと，SATソルバーをラップして，数独を楽に解けるようにした数独専用ソルバー

詳細は以下に載ってあるらしい．

https://qiita.com/okmt1230z/items/63f49e021c94077c343e

練習がてらpythonで
プログラムは以下のようにして数独の解を求めている．

1. Encording : txtファイルの数独情報からcnfファイルを作る
2. Solving : システムコールでSATソルバー clasp を起動してcnfファイルを解く
3. Decording : clasp のログを解析して，数独の答えを表示する

プログラムを実行したら，解きたい問題ファイルの入力を求められますので，ファイル名を入力してください．(懇願)
