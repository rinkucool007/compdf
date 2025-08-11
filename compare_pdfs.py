# compare_pdfs.py
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import os
import img2pdf
import io

def compare_and_annotate(pdf1_path, pdf2_path, output_pdf_path, compare_title="Comparison between 2 bills"):
    """
    Compare two PDFs, highlight differences, and generate a side-by-side annotated PDF.
    """
    comparison_report = []
    detailed_report = []

    def pdf_to_images(pdf_path, dpi=200):
        doc = fitz.open(pdf_path)
        images = []
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            images.append(img.convert("RGB"))
        doc.close()
        return images

    def draw_red_boxes(img1, img2, page_number):
        img1_cv = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2BGR)
        img2_cv = cv2.cvtColor(np.array(img2), cv2.COLOR_RGB2BGR)

        if img1_cv.shape != img2_cv.shape:
            height, width = max(img1_cv.shape[0], img2_cv.shape[0]), max(img1_cv.shape[1], img2_cv.shape[1])
            img1_cv = cv2.resize(img1_cv, (width, height))
            img2_cv = cv2.resize(img2_cv, (width, height))

        diff = cv2.absdiff(img1_cv, img2_cv)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        num_differences = len(contours)
        if num_differences > 0:
            comparison_report.append(f"Page {page_number}: Found {num_differences} difference(s).")
            detailed_report.append({
                'type': 'difference',
                'page': page_number,
                'message': f"{num_differences} difference(s) found."
            })
        else:
            comparison_report.append(f"Page {page_number}: No differences found.")
            detailed_report.append({
                'type': 'no_diff',
                'page': page_number,
                'message': "No visual differences detected."
            })

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(img2_cv, (x, y), (x + w, y + h), (0, 0, 255), 2)

        return Image.fromarray(cv2.cvtColor(img2_cv, cv2.COLOR_BGR2RGB))

    def create_side_by_side_image(img1, img2):
        w1, h1 = img1.size
        w2, h2 = img2.size
        combined_width = w1 + w2
        max_height = max(h1, h2)
        new_img = Image.new('RGB', (combined_width, max_height + 40), color=(255, 255, 255))
        new_img.paste(img1, (0, 40))
        new_img.paste(img2, (w1, 40))
        draw = ImageDraw.Draw(new_img)
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except IOError:
            font = ImageFont.load_default()
        draw.text((10, 5), compare_title, fill="black", font=font)
        return new_img

    def add_summary_page():
        summary_img = Image.new('RGB', (1200, 800), color=(255, 255, 255))
        draw = ImageDraw.Draw(summary_img)
        try:
            title_font = ImageFont.truetype("arial.ttf", 36)
            body_font = ImageFont.truetype("arial.ttf", 24)
        except:
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
        draw.text((50, 30), "🔍 Comparison Report Summary", fill="black", font=title_font)
        y = 100
        if not any(r['type'] == 'difference' for r in detailed_report):
            draw.text((50, y), "✅ No differences found between the documents.", fill="green", font=body_font)
        else:
            draw.text((50, y), "📌 Differences found:", fill="black", font=body_font)
            y += 40
            for entry in detailed_report:
                if entry['type'] == 'extra':
                    line = f"• Extra page in {entry['source']}, page {entry['page']}"
                elif entry['type'] == 'warning':
                    line = f"⚠️ {entry['message']}"
                else:
                    line = f"• Page {entry['page']}: {entry['message']}"
                draw.text((70, y), line, fill="black", font=body_font)
                y += 30
            draw.text((50, y + 20), "📝 Conclusion:", fill="black", font=body_font)
            y += 50
            draw.text((70, y), "Some pages show visual differences. Please review highlighted pages for details.",
                      fill="black", font=body_font)
        temp_path = "summary_page.jpg"
        summary_img.save(temp_path, "JPEG")
        return temp_path

    print("Converting PDFs to images...")
    try:
        images1 = pdf_to_images(pdf1_path)
        images2 = pdf_to_images(pdf2_path)
    except Exception as e:
        raise Exception(f"Error reading PDFs: {e}") from e

    if len(images1) != len(images2):
        print(f"⚠️ Warning: Page count differs: {len(images1)} vs {len(images2)}")
        detailed_report.append({
            'type': 'warning',
            'message': f"Page count differs: {len(images1)} vs {len(images2)}"
        })

    output_images = []

    print("Comparing pages...")
    for i, (img1, img2) in enumerate(zip(images1, images2)):
        print(f"Processing page {i+1}...")
        highlighted_img = draw_red_boxes(img1, img2, i+1)
        combined_img = create_side_by_side_image(img1, highlighted_img)
        temp_path = f"temp_page_{i}.jpg"
        combined_img.save(temp_path, "JPEG")
        output_images.append(temp_path)

    # Handle extra pages
    longer_pages = images1[len(images2):] if len(images1) > len(images2) else images2[len(images1):]
    source = "PDF1" if len(images1) > len(images2) else "PDF2"
    for j, extra_img in enumerate(longer_pages):
        page_num = (len(images1) if source == "PDF1" else len(images2)) + j + 1
        print(f"Adding extra page from {source}...")
        temp_path = os.path.join(temp_dir, f"temp_page_extra_{j}.jpg")
        extra_img.save(temp_path, "JPEG")
        output_images.append(temp_path)
        detailed_report.append({
            'page': page_num,
            'type': 'extra',
            'source': source,
            'message': f"Extra page in {source}, page {page_num}"
        })

    # Add summary
    summary_page = add_summary_page()
    output_images.append(summary_page)

    print("Generating final PDF...")
    try:
        with open(output_pdf_path, "wb") as f:
            f.write(img2pdf.convert(output_images))
    except Exception as e:
        raise Exception(f"Error generating PDF: {e}")

    # Cleanup
    for temp_file in output_images:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    print("✅ Temporary files cleaned up.")

    return output_pdf_path