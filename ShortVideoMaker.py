from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx.crop import crop
from moviepy.video.fx.resize import resize
from moviepy.video.io import VideoFileClip
from skimage.filters import gaussian


#    Relevant portion of clip to turn into short.
#    Values represent horizontal and vertical crop percentages respectively
__RELEVANT_VIDEO_POSITION_BY_GAME = {
    "COUNTER-STRIKE: GLOBAL OFFENSIVE": (0.50, 0),
    "COUNTER-STRIKE": (0.40, 0),
    "VALORANT": (0.45, 0)
}
# In case game is not in map get default value
__DEFAULT_CROP_PERCENTAGE = (0.5, 0)
#    Position of game feed to show.
#    Values represent upper left point (x, y) and the width and height [x, y, w, h]
__NORMALIZED_GAME_FEED_POSITION_BY_GAME = {
    "COUNTER-STRIKE: GLOBAL OFFENSIVE": [0.8854, 0.06481, 0.1146, 0.04629],
    "COUNTER-STRIKE": [0.8854, 0.06481, 0.1146, 0.04629],
    "VALORANT": [0.7604, 0.08333, 0.2395, 0.08333]
}


def blur(image):
    """ Returns a blurred (radius=5 pixels) version of the image """
    return gaussian(image.astype(float), sigma=5)


def make_short_blurry_background(clip: VideoFileClip, game: str) -> VideoFileClip:

    background_vid = make_short_default(clip)
    background_vid = background_vid.fl_image(blur)
    crop_percentage_horizontal, crop_percentage_vertical = \
        __RELEVANT_VIDEO_POSITION_BY_GAME.get(game.upper(), __DEFAULT_CROP_PERCENTAGE)
    center_vid = crop(clip,
                      x_center=clip.w / 2,
                      y_center=clip.h / 2,
                      width=clip.w * (1-crop_percentage_horizontal),
                      height=clip.h * (1-crop_percentage_vertical))
    center_vid = resize(center_vid, background_vid.w/center_vid.w).set_position("center")
    result = CompositeVideoClip([background_vid, center_vid])

    return result


def make_short_default(clip: VideoFileClip) -> VideoFileClip:
    return crop(clip, x_center=clip.w / 2, y_center=clip.h / 2, width=clip.h * (float(9) / 16), height=clip.h)


def make_short_with_game_feed(clip: VideoFileClip, game) -> VideoFileClip:
    background_vid = make_short_default(clip)
    background_vid = background_vid.fl_image(blur)
    crop_percentage_horizontal, crop_percentage_vertical = __RELEVANT_VIDEO_POSITION_BY_GAME.get(game.upper())
    center_vid = crop(clip,
                      x_center=clip.w / 2,
                      y_center=clip.h / 2,
                      width=clip.w * (1-crop_percentage_horizontal),
                      height=clip.h * (1-crop_percentage_vertical))
    center_vid = resize(center_vid, background_vid.w/center_vid.w)
    center_vid = center_vid.set_position("center")

    game_feed_position = get_game_feed_position(clip, game)
    game_feed = crop(clip,
                     x_center=int(game_feed_position[0]+(game_feed_position[2]/2)),
                     y_center=int(game_feed_position[1]+(game_feed_position[3]/2)),
                     width=game_feed_position[2],
                     height=game_feed_position[3])
    game_feed = resize(game_feed, background_vid.w * 0.75 / game_feed.w)
    game_feed = game_feed.set_position(("center", int((3*background_vid.h + center_vid.h - game_feed.h * 2)/4)))

    result = CompositeVideoClip([background_vid, center_vid, game_feed])
    return result


def get_game_feed_position(clip: VideoFileClip,
                           game: str):
    normalized_position = __NORMALIZED_GAME_FEED_POSITION_BY_GAME.get(game.upper())
    return [normalized_position[0] * clip.w,
            normalized_position[1] * clip.h,
            normalized_position[2] * clip.w,
            normalized_position[3] * clip.h]

# TODO: add more shorts layouts/presets

