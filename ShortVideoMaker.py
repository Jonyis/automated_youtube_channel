from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx.crop import crop
from moviepy.video.fx.resize import resize
from moviepy.video.io import VideoFileClip
from skimage.filters import gaussian


__CROP_PERCENTAGE_HORIZONTAL = 0.45
__CROP_PERCENTAGE_VERTICAL = 0


def blur(image):
    """ Returns a blurred (radius=5 pixels) version of the image """
    return gaussian(image.astype(float), sigma=5)


def make_short_blurry_background(clip: VideoFileClip) -> VideoFileClip:

    background_vid = make_short_default(clip)
    background_vid = background_vid.fl_image(blur)

    center_vid = crop(clip,
                      x_center=clip.w / 2,
                      y_center=clip.h / 2,
                      width=clip.w * (1-__CROP_PERCENTAGE_HORIZONTAL),
                      height=clip.h * (1-__CROP_PERCENTAGE_VERTICAL))
    center_vid = resize(center_vid, background_vid.w/center_vid.w).set_position("center")
    result = CompositeVideoClip([background_vid, center_vid])

    return result


def make_short_default(clip: VideoFileClip) -> VideoFileClip:
    return crop(clip, x_center=clip.w / 2, y_center=clip.h / 2, width=clip.h * (float(9) / 16), height=clip.h)
