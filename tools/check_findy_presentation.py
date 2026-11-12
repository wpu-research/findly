import argparse
import base64
import hashlib
import json
import re
import shutil
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--publish", type=Path)
    arguments = parser.parse_args()
    presentation = ROOT / "findy-yatirimci-sunumu-v2.html"
    document = presentation.read_text(encoding="utf-8")
    embedded_videos = re.findall(r'<source src="data:video/mp4;base64,([^"]+)"', document)
    expected_videos = [
        "gemini_generated_video_e3e40a4a.mp4",
        "gemini_generated_video_017ede88.mp4",
        "gemini_generated_video_91056a3b.mp4",
    ]
    assert len(embedded_videos) == 3
    for encoded, filename in zip(embedded_videos, expected_videos):
        original = ROOT / "assets" / "videos" / filename
        assert hashlib.sha256(base64.b64decode(encoded)).digest() == hashlib.sha256(original.read_bytes()).digest(), filename
    assert not re.search(r'(?:src|href)="(?:https?://|file://)', document)
    assert not re.search(r"\[(?:TARİH|AD SOYAD|FİYAT|TAM|SAM|SOM|TUTAR|YIL)\]", document)

    preview = ROOT / "validation" / "latest"
    preview.mkdir(parents=True, exist_ok=True)
    errors = []
    results = {"embedded_video_hashes": "3/3 originals match", "layouts": [], "videos": []}
    with sync_playwright() as runner:
        browser = runner.chromium.launch(
            executable_path="/opt/google/chrome/chrome",
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        page = browser.new_page(viewport={"width": 1440, "height": 1000}, reduced_motion="reduce")
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(presentation.as_uri(), wait_until="load", timeout=60000)
        page.evaluate("document.documentElement.style.scrollBehavior = 'auto'")
        assert page.locator("video").count() == 3
        assert page.locator("h1").inner_text().replace("\n", " ") == "Kalabalıkta birbirini bul."
        assert page.locator("[src]").evaluate_all("elements => elements.every(element => element.getAttribute('src').startsWith('data:'))")
        page.locator("img").evaluate_all("async images => { await Promise.all(images.map(image => { image.loading = 'eager'; return image.decode(); })); }")
        assert page.locator("img").evaluate_all("images => images.every(image => image.complete && image.naturalWidth > 0)")

        for section_id in ["giris", "video", "teknoloji", "yatirim"]:
            page.locator("#" + section_id).screenshot(path=str(preview / f"desktop-{section_id}.png"))

        for video_index in range(3):
            result = page.locator("video").nth(video_index).evaluate("""async video => {
              video.muted = true;
              await Promise.race([
                video.play(),
                new Promise((resolve, reject) => setTimeout(() => reject(new Error('Playback timeout')), 15000))
              ]);
              await new Promise(resolve => setTimeout(resolve, 500));
              const result = {width: video.videoWidth, height: video.videoHeight, duration: video.duration, currentTime: video.currentTime, readyState: video.readyState};
              video.pause();
              return result;
            }""")
            assert result["currentTime"] > 0 and result["readyState"] >= 2
            assert 9.5 < result["duration"] < 10.5
            results["videos"].append(result)

        page.locator("video").nth(0).evaluate("video => video.play()")
        page.locator("video").nth(1).evaluate("video => video.play()")
        assert page.locator("video").nth(0).evaluate("video => video.paused")
        page.locator("video").nth(1).evaluate("video => video.pause()")
        results["single_video_playback"] = "passed"

        page.evaluate("document.querySelector('#theme-toggle').click()")
        assert page.locator("html").get_attribute("data-theme") == "dark"
        page.locator("#video").screenshot(path=str(preview / "desktop-video-dark.png"))
        page.evaluate("document.querySelector('#theme-toggle').click()")
        assert page.locator("html").get_attribute("data-theme") == "light"

        for viewport_width in [1440, 1024, 768, 390, 360]:
            page.set_viewport_size({"width": viewport_width, "height": 900})
            page.wait_for_timeout(120)
            dimensions = page.evaluate("({viewport: innerWidth, content: document.documentElement.scrollWidth})")
            assert dimensions["content"] <= dimensions["viewport"], dimensions
            results["layouts"].append(dimensions)
        page.set_viewport_size({"width": 390, "height": 844})
        page.locator("#giris").screenshot(path=str(preview / "mobile-giris.png"))
        page.locator("#video").screenshot(path=str(preview / "mobile-video.png"))
        page.evaluate("scrollTo(0, 0)")
        page.locator("body").click(position={"x": 8, "y": 140})
        page.keyboard.press("ArrowRight")
        page.wait_for_timeout(150)
        assert abs(page.locator("#video").evaluate("section => section.getBoundingClientRect().top")) < 160
        assert not errors, errors
        browser.close()

    results["javascript_errors"] = errors
    if arguments.publish:
        if arguments.publish.exists():
            raise FileExistsError(f"Refusing to overwrite: {arguments.publish}")
        shutil.copy2(presentation, arguments.publish)
        assert hashlib.sha256(presentation.read_bytes()).digest() == hashlib.sha256(arguments.publish.read_bytes()).digest()
        results["published"] = str(arguments.publish)
    results["bytes"] = presentation.stat().st_size
    (preview / "validation.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
