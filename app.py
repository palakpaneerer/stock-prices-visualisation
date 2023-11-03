import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st

try:

    #関数設定
    @st.cache_data
    def get_data(days, tickers):
        df = pd.DataFrame()
    #for文で1企業ずつ株価データを取得する。
        for company in tickers.keys():
            #株価データ取得
            tkr = yf.Ticker(tickers[company])
            #ピリオド指定
            hist = tkr.history(period=f'{days}d')
            #日付データの表示方法変更
            hist.index = hist.index.strftime('%d %B %Y')
            #Closeデータのみ抽出
            hist = hist[['Close']]
            #コラム名を企業名に変更
            hist.columns = [company]
            #インデックスに企業名が来るように転置
            hist = hist.T
            #インデックス名をNameに変更
            hist.index.name = 'Name'
            #dfにデータを結合、加えていく。
            df = pd.concat([df, hist])
        return df

    #その他固定値設定
    tickers = {
            'apple': 'AAPL',
            'meta': 'META',
            'google': 'GOOGL',
            'microsoft': 'MSFT',
            'netflix': 'NFLX',
            'amazon': 'AMZN'
        }




    #タイトル
    st.title('米国株可視化アプリ')


    # サイドバー
    # 説明
    st.sidebar.write("""
    # 米国企業株価
    こちらは株価可視化ツールです。以下のオプションから表示日数を指定できます。
    """)

    # 表示日数設定
    st.sidebar.write("""
    ## 表示日数選択
    """)

    days = st.sidebar.slider('日数', 1, 50, 20)

    # 株価のグラフについて、y軸の上下の値設定
    st.sidebar.write("""
        ## 株価の範囲指定
        """)

    ymin, ymax = st.sidebar.slider(
        '範囲を指定してください',
        0.0, 3500.0, (0.0, 3500.0)
        )


    # 本文
    # サイドバーで選択した値に基づいたグラフデータ生成(関数実行)
    # ここではデータ生成だけであり、表示はしない。
    df = get_data(days, tickers)

    # インタラクティブな説明文（サイドバーで選択した日数を使用）
    st.write(f"""
    ### 過去 **{days}日間** の米国企業の株価 
    """)

    # マルチセレクトの表示（デフォルト値はgoogle,amazon,meta,apple）
    companies = st.multiselect(
        '会社名を選択してください。',
        list(df.index),
        ['google', 'amazon', 'meta', 'apple']
    )

    # マルチセレクトにて企業が1つも選ばれていない場合 → エラー
    # その他の場合、グラフ表示
    if not companies:
        st.error('少なくとも1社は選んでください。')
    else:
        # マルチセレクトで選んだ会社のデータを取得
        data = df.loc[companies]
        # グラフタイトルの表示
        st.write('### 株価 (USD)', data.sort_index())
        # グラフ可視化のためのデータセット整形
        data = data.T.reset_index()
        data = pd.melt(data, id_vars=['Date'])
        data = data.rename(columns={'value': 'Stock Price(USD)'})
        # グラフ生成
        chart = (
            alt.Chart(data)
            .mark_line(opacity=0.8, clip=True)
            .encode(
            x='Date:T',
            y=alt.Y('Stock Price(USD):Q', stack=None, scale=alt.Scale(domain=[ymin, ymax])),
            color='Name:N'
            )
        )
        # グラフ表示
        st.altair_chart(chart, use_container_width=True)

except:
    st.error('何かエラーが発生しています。')

