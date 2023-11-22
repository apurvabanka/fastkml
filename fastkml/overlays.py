"""
Overlays.
"""

import logging
from typing import Dict
from typing import Optional
from typing import Union

from fastkml import config
from fastkml import gx
from fastkml.enums import GridOrigin
from fastkml.enums import Shape
from fastkml.enums import Verbosity
from fastkml.features import _Feature
from fastkml.geometry import LinearRing
from fastkml.geometry import LineString
from fastkml.geometry import MultiGeometry
from fastkml.geometry import Point
from fastkml.geometry import Polygon
from fastkml.links import Icon
from fastkml.types import Element

logger = logging.getLogger(__name__)

KmlGeometry = Union[
    Point,
    LineString,
    LinearRing,
    Polygon,
    MultiGeometry,
    gx.MultiTrack,
    gx.Track,
]


class _Overlay(_Feature):
    """
    abstract element; do not create.

    Base type for image overlays drawn on the planet surface or on the screen

    A Container element holds one or more Features and allows the creation of
    nested hierarchies.
    """

    _color: Optional[str]
    # Color values expressed in hexadecimal notation, including opacity (alpha)
    # values. The order of expression is alphaOverlay, blue, green, red
    # (AABBGGRR). The range of values for any one color is 0 to 255 (00 to ff).
    # For opacity, 00 is fully transparent and ff is fully opaque.

    _draw_order: Optional[str]
    # Defines the stacking order for the images in overlapping overlays.
    # Overlays with higher <drawOrder> values are drawn on top of those with
    # lower <drawOrder> values.

    _icon: Optional[Icon]
    # Defines the image associated with the overlay. Contains an <href> html
    # tag which defines the location of the image to be used as the overlay.
    # The location can be either on a local file system or on a webserver. If
    # this element is omitted or contains no <href>, a rectangle is drawn using
    # the color and size defined by the ground or screen overlay.

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        color: Optional[str] = None,
        styles: None = None,
        style_url: Optional[str] = None,
        draw_order: Optional[str] = None,
        icon: Optional[Icon] = None,
    ) -> None:
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            name=name,
            description=description,
            styles=styles,
            style_url=style_url,
        )
        self._icon = icon
        self._color = color
        self._draw_order = draw_order

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color) -> None:
        if isinstance(color, str):
            self._color = color
        elif color is None:
            self._color = None
        else:
            raise ValueError

    @property
    def draw_order(self) -> Optional[str]:
        return self._draw_order

    @draw_order.setter
    def draw_order(self, value) -> None:
        if isinstance(value, (str, int, float)):
            self._draw_order = str(value)
        elif value is None:
            self._draw_order = None
        else:
            raise ValueError

    @property
    def icon(self) -> Optional[Icon]:
        return self._icon

    @icon.setter
    def icon(self, value) -> None:
        if isinstance(value, Icon):
            self._icon = value
        elif value is None:
            self._icon = None
        else:
            raise ValueError

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        if self._color:
            color = config.etree.SubElement(element, f"{self.ns}color")
            color.text = self._color
        if self._draw_order:
            draw_order = config.etree.SubElement(element, f"{self.ns}drawOrder")
            draw_order.text = self._draw_order
        if self._icon:
            element.append(self._icon.etree_element())
        return element

    def from_element(self, element: Element) -> None:
        super().from_element(element)
        color = element.find(f"{self.ns}color")
        if color is not None:
            self.color = color.text
        draw_order = element.find(f"{self.ns}drawOrder")
        if draw_order is not None:
            self.draw_order = draw_order.text
        icon = element.find(f"{self.ns}Icon")
        if icon is not None:
            self._icon = Icon.class_from_element(
                ns=self.ns,
                name_spaces=self.name_spaces,
                element=icon,
                strict=False,
            )


class PhotoOverlay(_Overlay):
    """
    The <PhotoOverlay> element allows you to geographically locate a photograph
    on the Earth and to specify viewing parameters for this PhotoOverlay.
    The PhotoOverlay can be a simple 2D rectangle, a partial or full cylinder,
    or a sphere (for spherical panoramas). The overlay is placed at the
    specified location and oriented toward the viewpoint.

    Because <PhotoOverlay> is derived from <Feature>, it can contain one of
    the two elements derived from <AbstractView>—either <Camera> or <LookAt>.
    The Camera (or LookAt) specifies a viewpoint and a viewing direction (also
    referred to as a view vector). The PhotoOverlay is positioned in relation
    to the viewpoint. Specifically, the plane of a 2D rectangular image is
    orthogonal (at right angles to) the view vector. The normal of this
    plane—that is, its front, which is the part
    with the photo—is oriented toward the viewpoint.

    The URL for the PhotoOverlay image is specified in the <Icon> tag,
    which is inherited from <Overlay>. The <Icon> tag must contain an <href>
    element that specifies the image file to use for the PhotoOverlay.
    In the case of a very large image, the <href> is a special URL that
    indexes into a pyramid of images of varying resolutions (see ImagePyramid).
    """

    __name__ = "PhotoOverlay"

    _rotation = None
    # Adjusts how the photo is placed inside the field of view. This element is
    # useful if your photo has been rotated and deviates slightly from a desired
    # horizontal view.

    # - ViewVolume -
    # Defines how much of the current scene is visible. Specifying the field of
    # view is analogous to specifying the lens opening in a physical camera.
    # A small field of view, like a telephoto lens, focuses on a small part of
    # the scene. A large field of view, like a wide-angle lens, focuses on a
    # large part of the scene.

    _left_fow = None
    # Angle, in degrees, between the camera's viewing direction and the left side
    # of the view volume.

    _right_fov = None
    # Angle, in degrees, between the camera's viewing direction and the right side
    # of the view volume.

    _bottom_fov = None
    # Angle, in degrees, between the camera's viewing direction and the bottom side
    # of the view volume.

    _top_fov = None
    # Angle, in degrees, between the camera's viewing direction and the top side
    # of the view volume.

    _near = None
    # Measurement in meters along the viewing direction from the camera viewpoint
    # to the PhotoOverlay shape.

    _tile_size = "256"
    # Size of the tiles, in pixels. Tiles must be square, and <tileSize> must
    # be a power of 2. A tile size of 256 (the default) or 512 is recommended.
    # The original image is divided into tiles of this size, at varying resolutions.

    _max_width = None
    # Width in pixels of the original image.

    _max_height = None
    # Height in pixels of the original image.

    _grid_origin: Optional[GridOrigin]
    # Specifies where to begin numbering the tiles in each layer of the pyramid.
    # A value of lowerLeft specifies that row 1, column 1 of each layer is in
    # the bottom left corner of the grid.

    _point: Optional[Point]
    # The <Point> element acts as a <Point> inside a <Placemark> element.
    # It draws an icon to mark the position of the PhotoOverlay.
    # The icon drawn is specified by the <styleUrl> and <StyleSelector> fields,
    # just as it is for <Placemark>.

    _shape: Optional[Shape]
    # The PhotoOverlay is projected onto the <shape>.
    # The <shape> can be one of the following:
    #   rectangle (default) -
    #       for an ordinary photo
    #   cylinder -
    #       for panoramas, which can be either partial or full cylinders
    #   sphere -
    #       for spherical panoramas

    @property
    def rotation(self) -> Optional[str]:
        return self._rotation

    @rotation.setter
    def rotation(self, value) -> None:
        if isinstance(value, (str, int, float)):
            self._rotation = str(value)
        elif value is None:
            self._rotation = None
        else:
            raise ValueError

    @property
    def left_fov(self) -> Optional[str]:
        return self._left_fow

    @left_fov.setter
    def left_fov(self, value) -> None:
        if isinstance(value, (str, int, float)):
            self._left_fow = str(value)
        elif value is None:
            self._left_fow = None
        else:
            raise ValueError

    @property
    def right_fov(self) -> Optional[str]:
        return self._right_fov

    @right_fov.setter
    def right_fov(self, value) -> None:
        if isinstance(value, (str, int, float)):
            self._right_fov = str(value)
        elif value is None:
            self._right_fov = None
        else:
            raise ValueError

    @property
    def bottom_fov(self) -> Optional[str]:
        return self._bottom_fov

    @bottom_fov.setter
    def bottom_fov(self, value) -> None:
        if isinstance(value, (str, int, float)):
            self._bottom_fov = str(value)
        elif value is None:
            self._bottom_fov = None
        else:
            raise ValueError

    @property
    def top_fov(self) -> Optional[str]:
        return self._top_fov

    @top_fov.setter
    def top_fov(self, value) -> None:
        if isinstance(value, (str, int, float)):
            self._top_fov = str(value)
        elif value is None:
            self._top_fov = None
        else:
            raise ValueError

    @property
    def near(self) -> Optional[str]:
        return self._near

    @near.setter
    def near(self, value) -> None:
        if isinstance(value, (str, int, float)):
            self._near = str(value)
        elif value is None:
            self._near = None
        else:
            raise ValueError

    @property
    def tile_size(self) -> Optional[str]:
        return self._tile_size

    @tile_size.setter
    def tile_size(self, value) -> None:
        if isinstance(value, (str, int, float)):
            self._tile_size = str(value)
        elif value is None:
            self._tile_size = None
        else:
            raise ValueError

    @property
    def max_width(self) -> Optional[str]:
        return self._max_width

    @max_width.setter
    def max_width(self, value) -> None:
        if isinstance(value, (str, int, float)):
            self._max_width = str(value)
        elif value is None:
            self._max_width = None
        else:
            raise ValueError

    @property
    def max_height(self) -> Optional[str]:
        return self._max_height

    @max_height.setter
    def max_height(self, value) -> None:
        if isinstance(value, (str, int, float)):
            self._max_height = str(value)
        elif value is None:
            self._max_height = None
        else:
            raise ValueError

    @property
    def grid_origin(self) -> Optional[GridOrigin]:
        return self._grid_origin

    @grid_origin.setter
    def grid_origin(self, value: Optional[GridOrigin]) -> None:
        self._grid_origin = value

    @property
    def point(self) -> str:
        return self._point

    @point.setter
    def point(self, value) -> None:
        if isinstance(value, (str, tuple)):
            self._point = str(value)
        else:
            raise ValueError

    @property
    def shape(self) -> Optional[Shape]:
        return self._shape

    @shape.setter
    def shape(self, value: Optional[Shape]) -> None:
        self._shape = value

    def view_volume(self, left_fov, right_fov, bottom_fov, top_fov, near) -> None:
        self.left_fov = left_fov
        self.right_fov = right_fov
        self.bottom_fov = bottom_fov
        self.top_fov = top_fov
        self.near = near

    def image_pyramid(self, tile_size, max_width, max_height, grid_origin) -> None:
        self.tile_size = tile_size
        self.max_width = max_width
        self.max_height = max_height
        self.grid_origin = grid_origin

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        if self._rotation:
            rotation = config.etree.SubElement(element, f"{self.ns}rotation")
            rotation.text = self._rotation
        if all(
            [
                self._left_fow,
                self._right_fov,
                self._bottom_fov,
                self._top_fov,
                self._near,
            ],
        ):
            view_volume = config.etree.SubElement(element, f"{self.ns}ViewVolume")
            left_fov = config.etree.SubElement(view_volume, f"{self.ns}leftFov")
            left_fov.text = self._left_fow
            right_fov = config.etree.SubElement(view_volume, f"{self.ns}rightFov")
            right_fov.text = self._right_fov
            bottom_fov = config.etree.SubElement(view_volume, f"{self.ns}bottomFov")
            bottom_fov.text = self._bottom_fov
            top_fov = config.etree.SubElement(view_volume, f"{self.ns}topFov")
            top_fov.text = self._top_fov
            near = config.etree.SubElement(view_volume, f"{self.ns}near")
            near.text = self._near
        if all([self._tile_size, self._max_width, self._max_height, self._grid_origin]):
            image_pyramid = config.etree.SubElement(element, f"{self.ns}ImagePyramid")
            tile_size = config.etree.SubElement(image_pyramid, f"{self.ns}tileSize")
            tile_size.text = self._tile_size
            max_width = config.etree.SubElement(image_pyramid, f"{self.ns}maxWidth")
            max_width.text = self._max_width
            max_height = config.etree.SubElement(image_pyramid, f"{self.ns}maxHeight")
            max_height.text = self._max_height
            grid_origin = config.etree.SubElement(image_pyramid, f"{self.ns}gridOrigin")
            grid_origin.text = self._grid_origin
        return element

    def from_element(self, element) -> None:
        super().from_element(element)
        rotation = element.find(f"{self.ns}rotation")
        if rotation is not None:
            self.rotation = rotation.text
        view_volume = element.find(f"{self.ns}ViewVolume")
        if view_volume is not None:
            left_fov = view_volume.find(f"{self.ns}leftFov")
            if left_fov is not None:
                self.left_fov = left_fov.text
            right_fov = view_volume.find(f"{self.ns}rightFov")
            if right_fov is not None:
                self.right_fov = right_fov.text
            bottom_fov = view_volume.find(f"{self.ns}bottomFov")
            if bottom_fov is not None:
                self.bottom_fov = bottom_fov.text
            top_fov = view_volume.find(f"{self.ns}topFov")
            if top_fov is not None:
                self.top_fov = top_fov.text
            near = view_volume.find(f"{self.ns}near")
            if near is not None:
                self.near = near.text
        image_pyramid = element.find(f"{self.ns}ImagePyramid")
        if image_pyramid is not None:
            tile_size = image_pyramid.find(f"{self.ns}tileSize")
            if tile_size is not None:
                self.tile_size = tile_size.text
            max_width = image_pyramid.find(f"{self.ns}maxWidth")
            if max_width is not None:
                self.max_width = max_width.text
            max_height = image_pyramid.find(f"{self.ns}maxHeight")
            if max_height is not None:
                self.max_height = max_height.text
            grid_origin = image_pyramid.find(f"{self.ns}gridOrigin")
            if grid_origin is not None:
                self.grid_origin = grid_origin.text
        point = element.find(f"{self.ns}Point")
        if point is not None:
            self.point = point.text
        shape = element.find(f"{self.ns}shape")
        if shape is not None:
            self.shape = shape.text


class GroundOverlay(_Overlay):
    """
    This element draws an image overlay draped onto the terrain. The <href>
    child of <Icon> specifies the image to be used as the overlay. This file
    can be either on a local file system or on a web server. If this element
    is omitted or contains no <href>, a rectangle is drawn using the color and
    LatLonBox bounds defined by the ground overlay.
    """

    __name__ = "GroundOverlay"

    _altitude = None
    # Specifies the distance above the earth's surface, in meters, and is
    # interpreted according to the altitude mode.

    _altitude_mode = "clampToGround"
    # Specifies how the <altitude> is interpreted. Possible values are:
    #   clampToGround -
    #       (default) Indicates to ignore the altitude specification and drape
    #       the overlay over the terrain.
    #   absolute -
    #       Sets the altitude of the overlay relative to sea level, regardless
    #       of the actual elevation of the terrain beneath the element. For
    #       example, if you set the altitude of an overlay to 10 meters with an
    #       absolute altitude mode, the overlay will appear to be at ground
    #       level if the terrain beneath is also 10 meters above sea level. If
    #       the terrain is 3 meters above sea level, the overlay will appear
    #       elevated above the terrain by 7 meters.

    # - LatLonBox -
    # TODO: Convert this to it's own class?
    # Specifies where the top, bottom, right, and left sides of a bounding box
    # for the ground overlay are aligned. Also, optionally the rotation of the
    # overlay.

    _north = None
    # Specifies the latitude of the north edge of the bounding box, in decimal
    # degrees from 0 to ±90.

    _south = None
    # Specifies the latitude of the south edge of the bounding box, in decimal
    # degrees from 0 to ±90.

    _east = None
    # Specifies the longitude of the east edge of the bounding box, in decimal
    # degrees from 0 to ±180. (For overlays that overlap the meridian of 180°
    # longitude, values can extend beyond that range.)

    _west = None
    # Specifies the longitude of the west edge of the bounding box, in decimal
    # degrees from 0 to ±180. (For overlays that overlap the meridian of 180°
    # longitude, values can extend beyond that range.)

    _rotation = None
    # Specifies a rotation of the overlay about its center, in degrees. Values
    # can be ±180. The default is 0 (north). Rotations are specified in a
    # counterclockwise direction.

    # TODO: <gx:LatLonQuad>
    # Used for nonrectangular quadrilateral ground overlays.
    _lat_lon_quad = None

    @property
    def altitude(self) -> Optional[str]:
        return self._altitude

    @altitude.setter
    def altitude(self, value) -> None:
        if isinstance(value, (str, int, float)):
            self._altitude = str(value)
        elif value is None:
            self._altitude = None
        else:
            raise ValueError

    @property
    def altitude_mode(self) -> str:
        return self._altitude_mode

    @altitude_mode.setter
    def altitude_mode(self, mode) -> None:
        if mode in ("clampToGround", "absolute"):
            self._altitude_mode = str(mode)
        else:
            self._altitude_mode = "clampToGround"

    @property
    def north(self) -> Optional[str]:
        return self._north

    @north.setter
    def north(self, value) -> None:
        if isinstance(value, (str, int, float)):
            self._north = str(value)
        elif value is None:
            self._north = None
        else:
            raise ValueError

    @property
    def south(self) -> Optional[str]:
        return self._south

    @south.setter
    def south(self, value) -> None:
        if isinstance(value, (str, int, float)):
            self._south = str(value)
        elif value is None:
            self._south = None
        else:
            raise ValueError

    @property
    def east(self) -> Optional[str]:
        return self._east

    @east.setter
    def east(self, value) -> None:
        if isinstance(value, (str, int, float)):
            self._east = str(value)
        elif value is None:
            self._east = None
        else:
            raise ValueError

    @property
    def west(self) -> Optional[str]:
        return self._west

    @west.setter
    def west(self, value) -> None:
        if isinstance(value, (str, int, float)):
            self._west = str(value)
        elif value is None:
            self._west = None
        else:
            raise ValueError

    @property
    def rotation(self) -> Optional[str]:
        return self._rotation

    @rotation.setter
    def rotation(self, value) -> None:
        if isinstance(value, (str, int, float)):
            self._rotation = str(value)
        elif value is None:
            self._rotation = None
        else:
            raise ValueError

    def lat_lon_box(
        self,
        north: int,
        south: int,
        east: int,
        west: int,
        rotation: int = 0,
    ) -> None:
        if -90 <= float(north) <= 90:
            self.north = north
        else:
            raise ValueError
        if -90 <= float(south) <= 90:
            self.south = south
        else:
            raise ValueError
        if -180 <= float(east) <= 180:
            self.east = east
        else:
            raise ValueError
        if -180 <= float(west) <= 180:
            self.west = west
        else:
            raise ValueError
        if -180 <= float(rotation) <= 180:
            self.rotation = rotation
        else:
            raise ValueError

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        if self._altitude:
            altitude = config.etree.SubElement(element, f"{self.ns}altitude")
            altitude.text = self._altitude
            if self._altitude_mode:
                altitude_mode = config.etree.SubElement(
                    element,
                    f"{self.ns}altitudeMode",
                )
                altitude_mode.text = self._altitude_mode
        if all([self._north, self._south, self._east, self._west]):
            lat_lon_box = config.etree.SubElement(element, f"{self.ns}LatLonBox")
            north = config.etree.SubElement(lat_lon_box, f"{self.ns}north")
            north.text = self._north
            south = config.etree.SubElement(lat_lon_box, f"{self.ns}south")
            south.text = self._south
            east = config.etree.SubElement(lat_lon_box, f"{self.ns}east")
            east.text = self._east
            west = config.etree.SubElement(lat_lon_box, f"{self.ns}west")
            west.text = self._west
            if self._rotation:
                rotation = config.etree.SubElement(lat_lon_box, f"{self.ns}rotation")
                rotation.text = self._rotation
        return element

    def from_element(self, element: Element) -> None:
        super().from_element(element)
        altitude = element.find(f"{self.ns}altitude")
        if altitude is not None:
            self.altitude = altitude.text
        altitude_mode = element.find(f"{self.ns}altitudeMode")
        if altitude_mode is not None:
            self.altitude_mode = altitude_mode.text
        lat_lon_box = element.find(f"{self.ns}LatLonBox")
        if lat_lon_box is not None:
            north = lat_lon_box.find(f"{self.ns}north")
            if north is not None:
                self.north = north.text
            south = lat_lon_box.find(f"{self.ns}south")
            if south is not None:
                self.south = south.text
            east = lat_lon_box.find(f"{self.ns}east")
            if east is not None:
                self.east = east.text
            west = lat_lon_box.find(f"{self.ns}west")
            if west is not None:
                self.west = west.text
            rotation = lat_lon_box.find(f"{self.ns}rotation")
            if rotation is not None:
                self.rotation = rotation.text
