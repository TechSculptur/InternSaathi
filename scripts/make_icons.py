import zlib
import struct
from pathlib import Path

def create_png(width, height, r, g, b, filename):
    # Minimal 24-bit PNG encoder
    raw_data = bytearray()
    for y in range(height):
        raw_data.append(0)  # Filter type 0 (None)
        for x in range(width):
            # Draw an emerald circle with orange center
            dx = x - width / 2
            dy = y - height / 2
            dist_sq = dx * dx + dy * dy
            radius_outer = (width * 0.45) ** 2
            radius_inner = (width * 0.15) ** 2
            if dist_sq <= radius_inner:
                raw_data.extend([245, 158, 11]) # Amber/orange
            elif dist_sq <= radius_outer:
                raw_data.extend([5, 150, 105])  # Emerald
            else:
                raw_data.extend([248, 250, 252]) # Light background

    def chunk(chunk_type, data):
        c = chunk_type + data
        crc = struct.pack(">I", zlib.crc32(c) & 0xffffffff)
        return struct.pack(">I", len(data)) + c + crc

    header = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    idat = zlib.compress(bytes(raw_data), 9)

    with open(filename, "wb") as f:
        f.write(header)
        f.write(chunk(b"IHDR", ihdr))
        f.write(chunk(b"IDAT", idat))
        f.write(chunk(b"IEND", b""))
    print(f"Generated {filename}")

if __name__ == "__main__":
    pub_dir = Path(__file__).resolve().parent.parent / "frontend" / "public"
    pub_dir.mkdir(parents=True, exist_ok=True)
    create_png(192, 192, 5, 150, 105, pub_dir / "icon-192.png")
    create_png(512, 512, 5, 150, 105, pub_dir / "icon-512.png")
