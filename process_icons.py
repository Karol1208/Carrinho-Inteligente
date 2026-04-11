from PIL import Image
import sys

def crop_center(img, x, y, w, h, output):
    cropped = img.crop((x, y, x + w, y + h))
    cropped.save(output)
    print(f"Saved {output}")

# Load sets
try:
    img_multi = Image.open(r"C:\Users\Aluno\.gemini\antigravity\brain\6ac17a32-ae36-4dea-adcb-ce13094d3af5\icon_users_alert_history_1775002001875.png")
    # Assuming they are side-by-side or in a grid. Let's guess standard 1024x1024 generation.
    # If 3 icons, they might be in a row. 
    # Horizontal: 0-341, 341-682, 682-1024
    width, height = img_multi.size
    w_part = width // 3
    crop_center(img_multi, 0, 0, w_part, height, r"c:\Users\Aluno\Documents\William Brito\carrinhoin\Carrinho-Inteligente\assets\icon_users.png")
    crop_center(img_multi, w_part, 0, w_part, height, r"c:\Users\Aluno\Documents\William Brito\carrinhoin\Carrinho-Inteligente\assets\icon_history.png")
    crop_center(img_multi, 2 * w_part, 0, w_part, height, r"c:\Users\Aluno\Documents\William Brito\carrinhoin\Carrinho-Inteligente\assets\icon_alert.png")

    img_rfid = Image.open(r"C:\Users\Aluno\.gemini\antigravity\brain\6ac17a32-ae36-4dea-adcb-ce13094d3af5\icon_rfid_status_1775002018410.png")
    # 2 icons. 0-512, 512-1024
    w_part_r = img_rfid.size[0] // 2
    h_r = img_rfid.size[1]
    crop_center(img_rfid, 0, 0, w_part_r, h_r, r"c:\Users\Aluno\Documents\William Brito\carrinhoin\Carrinho-Inteligente\assets\icon_rfid.png")
    crop_center(img_rfid, w_part_r, 0, w_part_r, h_r, r"c:\Users\Aluno\Documents\William Brito\carrinhoin\Carrinho-Inteligente\assets\icon_rfid_off.png")

    # Singular ones
    Image.open(r"C:\Users\Aluno\.gemini\antigravity\brain\6ac17a32-ae36-4dea-adcb-ce13094d3af5\icon_home_1775001967602.png").save(r"c:\Users\Aluno\Documents\William Brito\carrinhoin\Carrinho-Inteligente\assets\icon_home.png")
    Image.open(r"C:\Users\Aluno\.gemini\antigravity\brain\6ac17a32-ae36-4dea-adcb-ce13094d3af5\icon_inventory_1775001985505.png").save(r"c:\Users\Aluno\Documents\William Brito\carrinhoin\Carrinho-Inteligente\assets\icon_inventory.png")

    print("All icons processed.")
except Exception as e:
    print(f"Error: {e}")
