"""Overlays."""

import logging
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Optional
from typing import Union

from fastkml import atom
from fastkml import gx
from fastkml.base import _XMLObject
from fastkml.data import ExtendedData
from fastkml.enums import AltitudeMode
from fastkml.enums import GridOrigin
from fastkml.enums import Shape
from fastkml.enums import Verbosity
from fastkml.features import Snippet
from fastkml.features import _Feature
from fastkml.geometry import LinearRing
from fastkml.geometry import LineString
from fastkml.geometry import MultiGeometry
from fastkml.geometry import Point
from fastkml.geometry import Polygon
from fastkml.helpers import enum_subelement
from fastkml.helpers import float_subelement
from fastkml.helpers import int_subelement
from fastkml.helpers import subelement_enum_kwarg
from fastkml.helpers import subelement_float_kwarg
from fastkml.helpers import subelement_int_kwarg
from fastkml.helpers import subelement_text_kwarg
from fastkml.helpers import text_subelement
from fastkml.helpers import xml_subelement
from fastkml.helpers import xml_subelement_kwarg
from fastkml.links import Icon
from fastkml.styles import Style
from fastkml.styles import StyleMap
from fastkml.styles import StyleUrl
from fastkml.times import TimeSpan
from fastkml.times import TimeStamp
from fastkml.types import Element
from fastkml.views import Camera
from fastkml.views import LookAt
from fastkml.views import Region

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

    color: Optional[str]
    # Color values expressed in hexadecimal notation, including opacity (alpha)
    # values. The order of expression is alphaOverlay, blue, green, red
    # (AABBGGRR). The range of values for any one color is 0 to 255 (00 to ff).
    # For opacity, 00 is fully transparent and ff is fully opaque.

    draw_order: Optional[int]
    # Defines the stacking order for the images in overlapping overlays.
    # Overlays with higher <drawOrder> values are drawn on top of those with
    # lower <drawOrder> values.

    icon: Optional[Icon]
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
        visibility: Optional[bool] = None,
        isopen: Optional[bool] = None,
        atom_link: Optional[atom.Link] = None,
        atom_author: Optional[atom.Author] = None,
        address: Optional[str] = None,
        phone_number: Optional[str] = None,
        snippet: Optional[Snippet] = None,
        description: Optional[str] = None,
        view: Optional[Union[Camera, LookAt]] = None,
        times: Optional[Union[TimeSpan, TimeStamp]] = None,
        style_url: Optional[StyleUrl] = None,
        styles: Optional[Iterable[Union[Style, StyleMap]]] = None,
        region: Optional[Region] = None,
        extended_data: Optional[ExtendedData] = None,
        # Overlay specific
        color: Optional[str] = None,
        draw_order: Optional[int] = None,
        icon: Optional[Icon] = None,
    ) -> None:
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            name=name,
            visibility=visibility,
            isopen=isopen,
            atom_link=atom_link,
            atom_author=atom_author,
            address=address,
            phone_number=phone_number,
            snippet=snippet,
            description=description,
            view=view,
            times=times,
            style_url=style_url,
            styles=styles,
            region=region,
            extended_data=extended_data,
        )
        self.icon = icon
        self.color = color
        self.draw_order = draw_order

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        text_subelement(
            self,
            element=element,
            attr_name="color",
            node_name="color",
        )
        int_subelement(
            self,
            element=element,
            attr_name="draw_order",
            node_name="drawOrder",
        )
        xml_subelement(
            self,
            element=element,
            attr_name="icon",
            precision=precision,
            verbosity=verbosity,
        )
        return element

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        kwargs = super()._get_kwargs(
            ns=ns,
            name_spaces=name_spaces,
            element=element,
            strict=strict,
        )
        name_spaces = kwargs["name_spaces"]
        assert name_spaces is not None
        kwargs.update(
            subelement_text_kwarg(
                element=element,
                ns=ns,
                node_name="color",
                kwarg="color",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_int_kwarg(
                element=element,
                ns=ns,
                node_name="drawOrder",
                kwarg="draw_order",
                strict=strict,
            ),
        )
        kwargs.update(
            xml_subelement_kwarg(
                element=element,
                ns=ns,
                name_spaces=name_spaces,
                kwarg="icon",
                obj_class=Icon,
                strict=strict,
            ),
        )
        return kwargs


class ViewVolume(_XMLObject):
    """
    The ViewVolume defines how much of the current scene is visible.

    Specifying the field of view is analogous to specifying the lens opening in a
    physical camera.
    A small field of view, like a telephoto lens, focuses on a small part of the scene.
    A large field of view, like a wide-angle lens, focuses on a large part of the scene.

    https://developers.google.com/kml/documentation/kmlreference#viewvolume
    """

    left_fow: Optional[float]
    # Angle, in degrees, between the camera's viewing direction and the left side
    # of the view volume.

    right_fov: Optional[float]
    # Angle, in degrees, between the camera's viewing direction and the right side
    # of the view volume.

    bottom_fov: Optional[float]
    # Angle, in degrees, between the camera's viewing direction and the bottom side
    # of the view volume.

    top_fov: Optional[float]
    # Angle, in degrees, between the camera's viewing direction and the top side
    # of the view volume.

    near: Optional[float]
    # Measurement in meters along the viewing direction from the camera viewpoint
    # to the PhotoOverlay shape.

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        left_fov: Optional[float] = None,
        right_fov: Optional[float] = None,
        bottom_fov: Optional[float] = None,
        top_fov: Optional[float] = None,
        near: Optional[float] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces)
        self.left_fov = left_fov
        self.right_fov = right_fov
        self.bottom_fov = bottom_fov
        self.top_fov = top_fov
        self.near = near

    def __bool__(self) -> bool:
        return all(
            [
                self.left_fov is not None,
                self.right_fov is not None,
                self.bottom_fov is not None,
                self.top_fov is not None,
                self.near is not None,
            ],
        )

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        float_subelement(
            self,
            element=element,
            attr_name="left_fov",
            node_name="leftFov",
            precision=precision,
        )
        float_subelement(
            self,
            element=element,
            attr_name="right_fov",
            node_name="rightFov",
            precision=precision,
        )
        float_subelement(
            self,
            element=element,
            attr_name="bottom_fov",
            node_name="bottomFov",
            precision=precision,
        )
        float_subelement(
            self,
            element=element,
            attr_name="top_fov",
            node_name="topFov",
            precision=precision,
        )
        float_subelement(
            self,
            element=element,
            attr_name="near",
            node_name="near",
            precision=precision,
        )
        return element

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        kwargs = super()._get_kwargs(
            ns=ns,
            name_spaces=name_spaces,
            element=element,
            strict=strict,
        )
        name_spaces = kwargs["name_spaces"]
        assert name_spaces is not None
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="leftFov",
                kwarg="left_fov",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="rightFov",
                kwarg="right_fov",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="bottomFov",
                kwarg="bottom_fov",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="topFov",
                kwarg="top_fov",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="near",
                kwarg="near",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="near",
                kwarg="near",
                strict=strict,
            ),
        )

        return kwargs


class ImagePyramid(_XMLObject):
    """
    For very large images, you'll need to construct an image pyramid.

    An ImagePyramid is a hierarchical set of images, each of which is an increasingly
    lower resolution version of the original image.
    Each image in the pyramid is subdivided into tiles, so that only the portions in
    view need to be loaded.
    Google Earth calculates the current viewpoint and loads the tiles that are
    appropriate to the user's distance from the image.
    As the viewpoint moves closer to the PhotoOverlay, Google Earth loads higher
    resolution tiles.
    Since all the pixels in the original image can't be viewed on the screen at once,
    this preprocessing allows Google Earth to achieve maximum performance because it
    loads only the portions of the image that are in view, and only the pixel details
    that can be discerned by the user at the current viewpoint.

    When you specify an image pyramid, you also need to modify the <href> in the <Icon>
    element to include specifications for which tiles to load.
    """

    tile_size: Optional[int]
    # Size of the tiles, in pixels. Tiles must be square, and <tileSize> must be a power
    # of 2. A tile size of 256 (the default) or 512 is recommended.
    # The original image is divided into tiles of this size, at varying resolutions.

    max_width: Optional[int]
    # Width in pixels of the original image.

    max_height: Optional[int]
    # Height in pixels of the original image.

    grid_origin: Optional[GridOrigin]
    # Specifies where to begin numbering the tiles in each layer of the pyramid.
    # A value of lowerLeft specifies that row 1, column 1 of each layer is in
    # the bottom left corner of the grid.

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        tile_size: Optional[int] = None,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
        grid_origin: Optional[GridOrigin] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces)
        self.tile_size = tile_size
        self.max_width = max_width
        self.max_height = max_height
        self.grid_origin = grid_origin

    def __bool__(self) -> bool:
        return (
            self.tile_size is not None
            and self.max_width is not None
            and self.max_height is not None
            and self.grid_origin is not None
        )

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        int_subelement(
            self,
            element=element,
            attr_name="tile_size",
            node_name="tileSize",
        )
        int_subelement(
            self,
            element=element,
            attr_name="max_width",
            node_name="maxWidth",
        )
        int_subelement(
            self,
            element=element,
            attr_name="max_height",
            node_name="maxHeight",
        )
        enum_subelement(
            self,
            element=element,
            attr_name="grid_origin",
            node_name="gridOrigin",
        )

        return element

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        kwargs = super()._get_kwargs(
            ns=ns,
            name_spaces=name_spaces,
            element=element,
            strict=strict,
        )
        name_spaces = kwargs["name_spaces"]
        assert name_spaces is not None
        kwargs.update(
            subelement_int_kwarg(
                element=element,
                ns=ns,
                node_name="tileSize",
                kwarg="tile_size",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_int_kwarg(
                element=element,
                ns=ns,
                node_name="maxWidth",
                kwarg="max_width",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_int_kwarg(
                element=element,
                ns=ns,
                node_name="maxHeight",
                kwarg="max_height",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_enum_kwarg(
                element=element,
                ns=ns,
                node_name="gridOrigin",
                kwarg="grid_origin",
                enum_class=GridOrigin,
                strict=strict,
            ),
        )
        return kwargs


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

    https://developers.google.com/kml/documentation/kmlreference#photooverlay
    """

    rotation: Optional[float]
    # Adjusts how the photo is placed inside the field of view. This element is
    # useful if your photo has been rotated and deviates slightly from a desired
    # horizontal view.

    view_volume: Optional[ViewVolume]
    # Defines how much of the current scene is visible.

    image_pyramid: Optional[ImagePyramid]
    # Defines the format, resolution, and refresh rate for images that are
    # displayed in the PhotoOverlay.

    point: Optional[Point]
    # Defines the exact coordinates of the PhotoOverlay's origin, in latitude
    # and longitude, and in meters. Latitude and longitude measurements are
    # standard lat-lon projection with WGS84 datum. Altitude is distance above
    # the earth's surface, in meters, and is interpreted according to
    # altitudeMode.

    shape: Optional[Shape]
    # The PhotoOverlay is projected onto the <shape>.
    # The <shape> can be one of the following:
    #   rectangle (default) -
    #       for an ordinary photo
    #   cylinder -
    #       for panoramas, which can be either partial or full cylinders
    #   sphere -
    #       for spherical panoramas

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        name: Optional[str] = None,
        visibility: Optional[bool] = None,
        isopen: Optional[bool] = None,
        atom_link: Optional[atom.Link] = None,
        atom_author: Optional[atom.Author] = None,
        address: Optional[str] = None,
        phone_number: Optional[str] = None,
        snippet: Optional[Snippet] = None,
        description: Optional[str] = None,
        view: Optional[Union[Camera, LookAt]] = None,
        times: Optional[Union[TimeSpan, TimeStamp]] = None,
        style_url: Optional[StyleUrl] = None,
        styles: Optional[Iterable[Union[Style, StyleMap]]] = None,
        region: Optional[Region] = None,
        extended_data: Optional[ExtendedData] = None,
        color: Optional[str] = None,
        draw_order: Optional[int] = None,
        icon: Optional[Icon] = None,
        # Photo Overlay specific
        rotation: Optional[float] = None,
        view_volume: Optional[ViewVolume] = None,
        image_pyramid: Optional[ImagePyramid] = None,
        point: Optional[Point] = None,
        shape: Optional[Shape] = None,
    ) -> None:
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            name=name,
            visibility=visibility,
            isopen=isopen,
            atom_link=atom_link,
            atom_author=atom_author,
            address=address,
            phone_number=phone_number,
            snippet=snippet,
            description=description,
            view=view,
            times=times,
            style_url=style_url,
            styles=styles,
            region=region,
            extended_data=extended_data,
            color=color,
            draw_order=draw_order,
            icon=icon,
        )
        self.rotation = rotation
        self.view_volume = view_volume
        self.image_pyramid = image_pyramid
        self.point = point
        self.shape = shape

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        float_subelement(
            self,
            element=element,
            attr_name="rotation",
            node_name="rotation",
            precision=precision,
        )
        xml_subelement(
            self,
            element=element,
            attr_name="view_volume",
            precision=precision,
            verbosity=verbosity,
        )
        xml_subelement(
            self,
            element=element,
            attr_name="image_pyramid",
            precision=precision,
            verbosity=verbosity,
        )
        xml_subelement(
            self,
            element=element,
            attr_name="point",
            precision=precision,
            verbosity=verbosity,
        )
        enum_subelement(
            self,
            element=element,
            attr_name="shape",
            node_name="shape",
        )
        return element

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        kwargs = super()._get_kwargs(
            ns=ns,
            name_spaces=name_spaces,
            element=element,
            strict=strict,
        )
        name_spaces = kwargs["name_spaces"]
        assert name_spaces is not None
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="rotation",
                kwarg="rotation",
                strict=strict,
            ),
        )
        kwargs.update(
            xml_subelement_kwarg(
                element=element,
                ns=ns,
                name_spaces=name_spaces,
                kwarg="view_volume",
                obj_class=ViewVolume,
                strict=strict,
            ),
        )
        kwargs.update(
            xml_subelement_kwarg(
                element=element,
                ns=ns,
                name_spaces=name_spaces,
                kwarg="image_pyramid",
                obj_class=ImagePyramid,
                strict=strict,
            ),
        )
        kwargs.update(
            xml_subelement_kwarg(
                element=element,
                ns=ns,
                name_spaces=name_spaces,
                kwarg="point",
                obj_class=Point,
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_enum_kwarg(
                element=element,
                ns=ns,
                node_name="shape",
                kwarg="shape",
                enum_class=Shape,
                strict=strict,
            ),
        )

        return kwargs


class LatLonBox(_XMLObject):
    """
    Specifies where the top, bottom, right, and left sides of a bounding box for the
    ground overlay are aligned.
    Also, optionally the rotation of the overlay.

    <north> Specifies the latitude of the north edge of the bounding box,
    in decimal degrees from 0 to ±90.
    <south> Specifies the latitude of the south edge of the bounding box,
    in decimal degrees from 0 to ±90.
    <east> Specifies the longitude of the east edge of the bounding box,
    in decimal degrees from 0 to ±180.
    (For overlays that overlap the meridian of 180° longitude,
    values can extend beyond that range.)
    <west> Specifies the longitude of the west edge of the bounding box,
    in decimal degrees from 0 to ±180.
    (For overlays that overlap the meridian of 180° longitude,
    values can extend beyond that range.)
    <rotation> Specifies a rotation of the overlay about its center, in degrees.
    Values can be ±180. The default is 0 (north).
    Rotations are specified in a counterclockwise direction.
    """

    north: Optional[float]
    south: Optional[float]
    east: Optional[float]
    west: Optional[float]
    rotation: Optional[float]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        north: Optional[float] = None,
        south: Optional[float] = None,
        east: Optional[float] = None,
        west: Optional[float] = None,
        rotation: Optional[float] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces)
        self.north = north
        self.south = south
        self.east = east
        self.west = west
        self.rotation = rotation

    def __bool__(self) -> bool:
        return all(
            [
                self.north is not None,
                self.south is not None,
                self.east is not None,
                self.west is not None,
            ],
        )

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        float_subelement(
            self,
            element=element,
            attr_name="north",
            node_name="north",
            precision=precision,
        )
        float_subelement(
            self,
            element=element,
            attr_name="south",
            node_name="south",
            precision=precision,
        )
        float_subelement(
            self,
            element=element,
            attr_name="east",
            node_name="east",
            precision=precision,
        )
        float_subelement(
            self,
            element=element,
            attr_name="west",
            node_name="west",
            precision=precision,
        )
        float_subelement(
            self,
            element=element,
            attr_name="rotation",
            node_name="rotation",
            precision=precision,
        )

        return element

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        kwargs = super()._get_kwargs(
            ns=ns,
            name_spaces=name_spaces,
            element=element,
            strict=strict,
        )
        name_spaces = kwargs["name_spaces"]
        assert name_spaces is not None
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="north",
                kwarg="north",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="south",
                kwarg="south",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="east",
                kwarg="east",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="west",
                kwarg="west",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="rotation",
                kwarg="rotation",
                strict=strict,
            ),
        )
        return kwargs


class GroundOverlay(_Overlay):
    """
    This element draws an image overlay draped onto the terrain. The <href>
    child of <Icon> specifies the image to be used as the overlay. This file
    can be either on a local file system or on a web server. If this element
    is omitted or contains no <href>, a rectangle is drawn using the color and
    LatLonBox bounds defined by the ground overlay.

    https://developers.google.com/kml/documentation/kmlreference#groundoverlay
    """

    altitude: Optional[float]
    # Specifies the distance above the earth's surface, in meters, and is
    # interpreted according to the altitude mode.

    altitude_mode: Optional[AltitudeMode]
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

    lat_lon_box: Optional[LatLonBox]
    # Specifies where the top, bottom, right, and left sides of a bounding box
    # for the ground overlay are aligned. Also, optionally the rotation of the
    # overlay.

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        name: Optional[str] = None,
        visibility: Optional[bool] = None,
        isopen: Optional[bool] = None,
        atom_link: Optional[atom.Link] = None,
        atom_author: Optional[atom.Author] = None,
        address: Optional[str] = None,
        phone_number: Optional[str] = None,
        snippet: Optional[Snippet] = None,
        description: Optional[str] = None,
        view: Optional[Union[Camera, LookAt]] = None,
        times: Optional[Union[TimeSpan, TimeStamp]] = None,
        style_url: Optional[StyleUrl] = None,
        styles: Optional[Iterable[Union[Style, StyleMap]]] = None,
        region: Optional[Region] = None,
        extended_data: Optional[ExtendedData] = None,
        color: Optional[str] = None,
        draw_order: Optional[int] = None,
        icon: Optional[Icon] = None,
        # Ground Overlay specific
        altitude: Optional[float] = None,
        altitude_mode: Optional[AltitudeMode] = None,
        lat_lon_box: Optional[LatLonBox] = None,
    ) -> None:
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            name=name,
            visibility=visibility,
            isopen=isopen,
            atom_link=atom_link,
            atom_author=atom_author,
            address=address,
            phone_number=phone_number,
            snippet=snippet,
            description=description,
            view=view,
            times=times,
            style_url=style_url,
            styles=styles,
            region=region,
            extended_data=extended_data,
            color=color,
            draw_order=draw_order,
            icon=icon,
        )
        self.altitude = altitude
        self.altitude_mode = altitude_mode
        self.lat_lon_box = lat_lon_box

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        float_subelement(
            self,
            element=element,
            attr_name="altitude",
            node_name="altitude",
            precision=precision,
        )
        enum_subelement(
            self,
            element=element,
            attr_name="altitude_mode",
            node_name="altitudeMode",
        )
        xml_subelement(
            self,
            element=element,
            attr_name="lat_lon_box",
            precision=precision,
            verbosity=verbosity,
        )
        return element

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        kwargs = super()._get_kwargs(
            ns=ns,
            name_spaces=name_spaces,
            element=element,
            strict=strict,
        )
        name_spaces = kwargs["name_spaces"]
        assert name_spaces is not None
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="altitude",
                kwarg="altitude",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_enum_kwarg(
                element=element,
                ns=ns,
                node_name="altitudeMode",
                kwarg="altitude_mode",
                enum_class=AltitudeMode,
                strict=strict,
            ),
        )
        kwargs.update(
            xml_subelement_kwarg(
                element=element,
                ns=ns,
                name_spaces=name_spaces,
                kwarg="lat_lon_box",
                obj_class=LatLonBox,
                strict=strict,
            ),
        )

        return kwargs
