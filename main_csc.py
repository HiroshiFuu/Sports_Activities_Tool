import sys
import traceback

from csc_booking import CSC


def main():
    timed = None
    if len(sys.argv) == 5:
        timed = sys.argv[4]
    try:
        csc = CSC()
        csc.court_booking(sys.argv[1], sys.argv[2], sys.argv[3], timed)
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    main()

# python -m PyInstaller --name "CSC Booking" -F "D:\\AAA\\Sports_Activities_Tool\\main_csc.py"
