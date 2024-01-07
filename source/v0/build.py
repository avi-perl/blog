import shutil
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader


# Set up Jinja environment
template_dir = "."  # Change this to the directory where your template file is located
env = Environment(loader=FileSystemLoader(template_dir))

version = "v0"
dir = f"/{version}"
head = {"stylesheet": f"{dir}/src/style.css"}
header = {"img_source": f"{dir}/img/beta_header.png"}


def content_to_html(content: list[dict], slug: str):
    html_content = ""
    for item in content:
        if item["type"] == "html":
            html_content += item["content"]
        elif item["type"] == "img":
            content_path = f'{version}/img/{slug}/'
            Path(content_path).mkdir(exist_ok=True, parents=True)
            img_path = f'{content_path}{item["path"].name}'
            shutil.copy(item["path"], content_path)
            html_content += f'<img src="/{img_path}">'

    return html_content


def dir_to_post_data(path: Path) -> dict[str, Any]:
    """Convert a folder into the data needed for a post"""
    return_data = {
        "slug": path.name.split("__")[-1].replace(" ", "-"),
        "content": [],
    }
    content = []

    for current_path in path.iterdir():
        if current_path.is_file():
            if current_path.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                content.append({
                    "type": "img",
                    "path": current_path
                })
            elif current_path.suffix.lower() in [".html"] \
                    and current_path.name.lower() not in ["post.html", "preview.html"]:
                content.append({
                    "type": "html",
                    "content": current_path.read_text()
                })

        if current_path.name.startswith("post"):
            return_data["post"] = current_path.read_text() if current_path.is_file() \
                else dir_to_post_data(current_path)["post"]
        else:
            return_data["post"] = content_to_html(content, return_data["slug"])

        if current_path.name.startswith("preview"):
            return_data["preview"] = current_path.read_text() if current_path.is_file() \
                else dir_to_post_data(current_path)["preview"]
        else:
            return_data["preview"] = content_to_html(content, return_data["slug"])

    print(return_data)
    return return_data


if __name__ == "__main__":
    posts = []
    for directory in Path("posts/").iterdir():
        if directory.is_dir():
            posts.append(dir_to_post_data(directory))

    data = {
        "dir": dir,
        "head": head,
        "header": header,
        "posts": posts[::-1],
    }

    # Render the listing page
    template = env.get_template('templates/list_page.html')
    output = template.render(data)

    Path(dir).mkdir(exist_ok=True)
    with open('v0/index.html', 'w') as file:
        file.write(output)

    with open('index.html', 'w') as file:
        file.write(output)

    # Render the blog pages
    for post in data.get("posts", []):
        post = {**data, **post}
        template = env.get_template('templates/post_page.html')
        output = template.render(post)

        Path("v0/posts/").mkdir(exist_ok=True)
        filename = f'{post.get("slug")}.html'
        with open(f'v0/posts/{filename}', 'w') as file:
            file.write(output)

    # shutil.copytree(version, Path("../../") / version, dirs_exist_ok=True)
