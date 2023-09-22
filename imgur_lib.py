from imgurpython import ImgurClient as BaseImgurClient
import base64

class ImgurClient(BaseImgurClient):
    def get_image_links(self, album_id: str) -> list[str]: 
        album_id = self.get_album(album_id)
        links = map(lambda image_data: image_data['link'], album_id.images)
        return list(links)

    def upload_image_to_album(self, image: bytes, album_id: str) -> None:
        b64 = base64.b64encode(image)
        data = {
            'image': b64,
            'type': 'base64',
            'album': album_id,
        }
        self.make_request('POST', 'upload', data, False)

    def parse_file_link(self, album_id: str, filepos: int) -> None:
        photo_list = self.get_image_links(album_id)
        parsed_link = photo_list[-1].split("/")
        filename = parsed_link[filepos]
        parsed_filename = filename.split('.')
        file_id = parsed_filename[0]
        return file_id