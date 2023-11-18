from quart import (
    Quart,
    redirect,
    send_from_directory,
    url_for,
    render_template,
    flash,
    request,
)
from quart_wtf.csrf import CSRFProtect
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os
from werkzeug.utils import secure_filename
import codecs
from .forms import EncodeForm, DecodeForm, EncodeFileForm
from .utils import encode, decode, rename, get_text_from_file, write_text_to_file

load_dotenv(dotenv_path=".env")

app = Quart(__name__)
csrf = CSRFProtect(app)
app.config[
    "SECRET_KEY"
] = "442cca115de8939240fd9531607188e8790f5eb49afdc8e7f064e1ce8f22772e"  # os.getenv("SECRET_KEY")
app.config["WTF_CSRF_ENABLED"] = os.getenv("WTF_CSRF_ENABLED")

# Fernet
key = Fernet.generate_key()
fernet = Fernet(key)


def run() -> None:
    app.run(debug=False, use_reloader=True)


@app.route("/", methods=["GET", "POST"])
async def index():
    encode_form = await EncodeForm().create_form()
    decode_form = await DecodeForm().create_form()

    if await encode_form.validate_on_submit():
        secret_text = fernet.encrypt(encode_form.secret_text.data.encode()).decode()
        image = encode_form.image.data
        filename = secure_filename(image.filename)
        await image.save(os.path.join(app.instance_path, "inputs", filename))

        # rename file to random name
        filename = await rename(filename, os.path.join(app.instance_path, "inputs"))

        # encode text to image
        await encode(
            os.path.join(app.instance_path, "inputs", filename),
            os.path.join(app.instance_path, "outputs", filename),
            secret_text,
        )

        # delete input file
        # os.remove(os.path.join(app.instance_path, "inputs", filename))

        await flash("Image encoded successfully, please download your image", "success")
        return await render_template(
            "index.html",
            encode_form=encode_form,
            decode_form=decode_form,
            filename=filename,
            title="Image Steganography - For text",
        )

    if await decode_form.validate_on_submit():
        image = decode_form.image.data
        filename = secure_filename(image.filename)
        await image.save(os.path.join(app.instance_path, "inputs", filename))

        # rename file to random name
        filename = await rename(filename, os.path.join(app.instance_path, "inputs"))

        # decode text from image
        decoded_text = fernet.decrypt(
            await decode(
                os.path.join(app.instance_path, "inputs", filename),
            )
        ).decode()

        # delete input file
        # os.remove(os.path.join(app.instance_path, "inputs", filename))

        await flash("Image decoded successfully", "success")
        return await render_template(
            "index.html",
            encode_form=encode_form,
            decode_form=decode_form,
            decoded_text=decoded_text,
            title="Image Steganography - For text",
        )

    return await render_template(
        "index.html",
        encode_form=encode_form,
        decode_form=decode_form,
        title="Image Steganography - For text",
    )


@app.route("/file", methods=["GET", "POST"])
async def file():
    encode_form = await EncodeFileForm().create_form()
    decode_form = await DecodeForm().create_form()

    if await encode_form.validate_on_submit():
        secret_file = encode_form.text_file.data
        image = encode_form.image.data
        image_filename = secure_filename(image.filename)
        secret_filename = secure_filename(secret_file.filename)
        await image.save(os.path.join(app.instance_path, "inputs", image_filename))
        await secret_file.save(
            os.path.join(app.instance_path, "inputs", secret_filename)
        )
        # rename file to random name
        image_filename = await rename(
            image_filename, os.path.join(app.instance_path, "inputs")
        )
        secret_filename = await rename(
            secret_filename, os.path.join(app.instance_path, "inputs")
        )

        # get text in secret file
        secret_text = await get_text_from_file(
            os.path.join(app.instance_path, "inputs", secret_filename)
        )

        if secret_text == "":
            await flash("Text file is empty", "danger")
            return await render_template(
                "file.html",
                title="Image Steganography - For file",
                encode_form=encode_form,
                decode_form=decode_form,
            )
        elif len(secret_text) > 500:
            await flash("Text file is too long", "danger")
            return await render_template(
                "file.html",
                title="Image Steganography - For file",
                encode_form=encode_form,
                decode_form=decode_form,
            )

        # encode text to image
        await encode(
            os.path.join(app.instance_path, "inputs", image_filename),
            os.path.join(app.instance_path, "outputs", image_filename),
            fernet.encrypt(secret_text.encode()).decode(),
        )

        # delete input file
        # os.remove(os.path.join(app.instance_path, "inputs", image_filename))

        await flash("Image encoded successfully, please download your image", "success")
        return await render_template(
            "file.html",
            title="Image Steganography - For file",
            encode_form=encode_form,
            decode_form=decode_form,
            image_filename=image_filename,
        )

    if await decode_form.validate_on_submit():
        image = decode_form.image.data
        image_filename = secure_filename(image.filename)
        await image.save(os.path.join(app.instance_path, "inputs", image_filename))

        # rename file to random name
        image_filename = await rename(
            image_filename, os.path.join(app.instance_path, "inputs")
        )

        # decode text from image
        decoded_text = fernet.decrypt(
            await decode(
                os.path.join(app.instance_path, "inputs", image_filename),
            )
        ).decode()

        # write text to file
        await write_text_to_file(
            os.path.join(
                app.instance_path, "outputs", f"{image_filename.split('.')[0]}.txt"
            ),
            decoded_text,
        )

        # delete input file
        # os.remove(os.path.join(app.instance_path, "inputs", image_filename))

        await flash("Image decoded successfully", "success")
        return await render_template(
            "file.html",
            title="Image Steganography - For file",
            encode_form=encode_form,
            decode_form=decode_form,
            decoded_file=f"{image_filename.split('.')[0]}.txt",
        )

    return await render_template(
        "file.html",
        title="Image Steganography - For file",
        encode_form=encode_form,
        decode_form=decode_form,
    )


@app.route("/uploads/<path:filename>", methods=["GET", "POST"])
async def download(filename: str):
    uploads = os.path.join(app.instance_path, "outputs")
    return await send_from_directory(directory=uploads, file_name=filename)
