from blessed import Terminal

term = Terminal()

print("Mouse supported:", term.does_mouse())
print("Click inside the terminal. Press Q to quit.")

with term.cbreak(), term.mouse_enabled():
    while True:
        val = term.inkey()

        if val.lower() == "q":
            break

        if val.name and val.name.startswith("MOUSE_"):
            x,y = val.mouse_xy
            print(
                f"Button: {val.name}, "
                f"x={x}, y={x}"
            )