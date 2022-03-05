from json import load, dump


async def load_predictions():
    """load the predictions json data from predictions.json"""
    with open("./data/predictions.json") as f:
        return load(f)


async def clear_predictions():
    """clear all predictions and load json back to defaul"""
    data = {}
    data["open"] = False
    data["currency"] = "USD"
    data["predictions"] = []
    await dump_predictions(data)


async def dump_predictions(data):
    """dump the predictions data to predictions.json"""
    with open("./data/predictions.json", "w") as f:
        dump(data, f, indent=4)
