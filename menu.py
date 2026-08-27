from config import *


def draw_menu(game) -> None:
    game.canvas.delete("all")
    game.menu_items.clear()

    title = game.canvas.create_text(
        VISIBLE_WIDTH // 2, 120,
        text="SURVIVAL GROUNDS",
        fill="white",
        font=("Courier", 48, "bold")
    )
    game.menu_items.append(title)

    if game.menu_state == "map":
        subtitle = game.canvas.create_text(
            VISIBLE_WIDTH // 2, 220,
            text="Select Map Type",
            fill="white",
            font=("Courier", 32, "bold")
        )
        game.menu_items.append(subtitle)

        for i, text in enumerate(game.map_options):
            color = HIGHLIGHT_COLOR if i == game.map_index else NORMAL_COLOR
            item = game.canvas.create_text(
                VISIBLE_WIDTH // 2, 320 + i * 60,
                text=text,
                fill=color,
                font=("Courier", 28, "bold")
            )
            game.menu_items.append(item)

    elif game.menu_state == "difficulty":
        subtitle = game.canvas.create_text(
            VISIBLE_WIDTH // 2, 220,
            text="Select Difficulty",
            fill="white",
            font=("Courier", 32, "bold")
        )
        game.menu_items.append(subtitle)

        for i, text in enumerate(game.diff_options):
            color = HIGHLIGHT_COLOR if i == game.diff_index else NORMAL_COLOR
            item = game.canvas.create_text(
                VISIBLE_WIDTH // 2, 320 + i * 60,
                text=text,
                fill=color,
                font=("Courier", 28, "bold")
            )
            game.menu_items.append(item)


def handle_menu_input(game, key: str) -> None:
    if game.menu_state == "map":
        if key == "up":
            game.map_index = (game.map_index - 1) % len(game.map_options)
            draw_menu(game)
        elif key == "down":
            game.map_index = (game.map_index + 1) % len(game.map_options)
            draw_menu(game)
        elif key == "return":
            game.terrain_choice = "A" if game.map_index == 0 else "B"
            game.menu_state = "difficulty"
            draw_menu(game)

    elif game.menu_state == "difficulty":
        if key == "up":
            game.diff_index = (game.diff_index - 1) % len(game.diff_options)
            draw_menu(game)
        elif key == "down":
            game.diff_index = (game.diff_index + 1) % len(game.diff_options)
            draw_menu(game)
        elif key == "return":
            game.difficulty_choice = "easy" if game.diff_index == 0 else "normal"
            game.menu_active = False
            game.start_game()
