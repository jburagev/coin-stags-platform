var chart = LightweightCharts.createChart(document.getElementById('chart'), {
        width:  1200,
        height: 400,
        layout: {
                backgroundColor: '#000000',
                textColor: 'rgba(255, 255, 255, 0.9)',
        },
        grid: {
                vertLines: {
                        color: 'rgba(197, 203, 206, 0.5)',
                },
                horzLines: {
                        color: 'rgba(197, 203, 206, 0.5)',
                },
        },
        crosshair: {
                mode: LightweightCharts.CrosshairMode.Normal,
        },
        rightPriceScale: {
                borderColor: 'rgba(197, 203, 206, 0.8)',
        },
        timeScale: {
                borderColor: 'rgba(197, 203, 206, 0.8)',
        },
});

var result = LightweightCharts.createChart(document.getElementById('result'), {
    width: 1200,
    height: 200,
    layout: {
        backgroundColor: '#000000',
        textColor: 'rgba(255, 255, 255, 0.9)',
    },
    grid: {
        vertLines: {
            color: 'rgba(197, 203, 206, 0.5)',
        },
        horzLines: {
            color: 'rgba(197, 203, 206, 0.5)',
        },
    },
    crosshair: {
        mode: LightweightCharts.CrosshairMode.Normal,
    },
    rightPriceScale: {
        borderColor: 'rgba(197, 203, 206, 0.8)',
    },
    timeScale: {
        borderColor: 'rgba(197, 203, 206, 0.8)',
    },
});

var indicator = LightweightCharts.createChart(document.getElementById('indicator'), {
    width: 1200,
    height: 200,
    layout: {
        backgroundColor: '#000000',
        textColor: 'rgba(255, 255, 255, 0.9)',
    },
    grid: {
        vertLines: {
            color: 'rgba(197, 203, 206, 0.5)',
        },
        horzLines: {
            color: 'rgba(197, 203, 206, 0.5)',
        },
    },
    crosshair: {
        mode: LightweightCharts.CrosshairMode.Normal,
    },
    rightPriceScale: {
        borderColor: 'rgba(197, 203, 206, 0.8)',
    },
    timeScale: {
        borderColor: 'rgba(197, 203, 206, 0.8)',
    },
});

var candleSeries = chart.addCandlestickSeries({
  upColor: 'rgba(255, 144, 0, 1)',
  downColor: '#000',
  borderDownColor: 'rgba(255, 144, 0, 1)',
  borderUpColor: 'rgba(255, 144, 0, 1)',
  wickDownColor: 'rgba(255, 144, 0, 1)',
  wickUpColor: 'rgba(255, 144, 0, 1)',
});

var lineSeries = indicator.addLineSeries({
    lineColor: 'rgba(19, 40, 153, 1.0)',
    lineWidth: 4,
});

var areaSeries = result.addAreaSeries({
    topColor: 'rgba(19, 68, 193, 0.4)',
    bottomColor: 'rgba(0, 120, 255, 0.0)',
    lineColor: 'rgba(19, 40, 153, 1.0)',
    lineWidth: 3
});

fetch('http://127.0.0.1:5000/history')
    .then((r) => r.json())
    .then((response) => {
        console.log(response)

        candleSeries.setData(response);
    })

fetch('http://127.0.0.1:5000/strategy')
    .then((r) => r.json())
    .then((response) => {
        console.log(response)

        lineSeries.setData(response);
    })

var binanceSocket = new WebSocket("wss://stream.binance.com:9443/ws/btcusdt@kline_15m");

binanceSocket.onmessage = function (event) {
    var message = JSON.parse(event.data);

    var candlestick = message.k;

    //namesto fetch na tem mestu bo potrebno run python strategije in dobiti samo zadnjo cifro, ne pa popolnoma now array

    fetch('http://127.0.0.1:5000/tick')
        .then((r) => r.json())
        .then((response) => {
            console.log(response)

            lineSeries.update(response);
        })

    candleSeries.update({
        "time": candlestick.t / 1000,
        "open": candlestick.o,
        "high": candlestick.h,
        "low": candlestick.l,
        "close": candlestick.c
    })
}

const button = document.getElementById("backtest")
button.addEventListener("click", changeResult, false);

function changeResult() {
    fetch('http://127.0.0.1:5000/backtest')
        .then((r) => r.json())
        .then((response) => {
            console.log(response);
            areaSeries.length = 0;
            areaSeries.setData(response);
        })
}