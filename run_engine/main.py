from run_engine.core.loop import RunLoop


def main():

    engine = RunLoop()

    print("STARTING STOCHASTIC DRY RUN ENGINE")

    tick = 0

    while True:

        try:
            # FIX: build proper tick object
            tick_data = {
                "tick": tick,
                "price": 30000 + (tick % 100)  # synthetic but stable price stream
            }

            result = engine.step(tick_data)

            if result:
                print(result)

            tick += 1

        except Exception as e:
            print(f"[CRASH] {str(e)}")
            tick += 1


if __name__ == "__main__":
    main()