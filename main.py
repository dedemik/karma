"""Bilgisayar simülasyonu: Windows / macOS / GNOME masaüstü.

Çalıştırmak için:
    python main.py
"""

from sim.desktop import Desktop


def main() -> None:
    Desktop().run()


if __name__ == "__main__":
    main()
