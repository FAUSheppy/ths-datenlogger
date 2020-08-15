#!/usr/bin/python3
import frontend
import sys
if __name__ == "__main__":
        try:
            frontend.main()
            #input("Done! <ENTER> to exit")
            sys.exit(0)
        except KeyboardInterrupt as e:
            sys.exit(1)
        except Exception as e:
            print(e)
            input("Ein Fehler ist aufgetreten, <ENTER> um zu beenden, wenn dieser Fehler unerwartet war -> Mail!")
            sys.exit(1)
