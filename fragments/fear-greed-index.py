import requests
import pandas as pd


def get_fear_greedy_index():
    url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
    resp = requests.get(url=url, headers={
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "origin": "https://edition.cnn.com"
    })
    res = resp.json()
    df = pd.DataFrame.from_records(res["fear_and_greed_historical"]["data"], columns=['x', 'y', 'rating'])
    df = df.rename(columns={"x": "date", "y": "fear_and_greed"})
    return df


if __name__ == '__main__':
    df = get_fear_greedy_index()
    print(df)
