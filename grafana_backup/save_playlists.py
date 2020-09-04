import os
import json
from grafana_backup.dashboardApi import search_playlists, get_playlist
from grafana_backup.commons import to_python2_and_3_compatible_string, print_horizontal_line, save_json


def main(args, settings):
    backup_dir = settings.get('BACKUP_DIR')
    timestamp_output = settings.get('TIMESTAMP_OUTPUT')
    timestamp = settings.get('TIMESTAMP')
    grafana_url = settings.get('GRAFANA_URL')
    http_get_headers = settings.get('HTTP_GET_HEADERS')
    verify_ssl = settings.get('VERIFY_SSL')
    client_cert = settings.get('CLIENT_CERT')
    debug = settings.get('DEBUG')
    pretty_print = settings.get('PRETTY_PRINT')

    if timestamp_output:
        folder_path = '{0}/playlists/{1}'.format(backup_dir, timestamp)
        log_file = 'playlists_{0}.txt'.format(timestamp)
    else:
        folder_path = '{0}/playlists'.format(backup_dir)
        log_file = 'playlists.txt'


    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    playlists = get_all_playlists_in_grafana(grafana_url, http_get_headers, verify_ssl, client_cert, debug)
    print_horizontal_line()
    get_individual_playlist_setting_and_save(playlists, folder_path, log_file, grafana_url, http_get_headers, verify_ssl, client_cert, debug, pretty_print)
    print_horizontal_line()


def get_all_playlists_in_grafana(grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    status_and_content_of_all_playlists = search_playlists(grafana_url, http_get_headers, verify_ssl, client_cert, debug)
    status = status_and_content_of_all_playlists[0]
    content = status_and_content_of_all_playlists[1]
    if status == 200:
        playlists = content
        print("There are {0} playlists:".format(len(content)))
        for playlist in playlists:
            print("name: {0}".format(to_python2_and_3_compatible_string(playlist['name'])))
        return playlists
    else:
        print("get playlists failed, status: {0}, msg: {1}".format(status, content))
        return []


def save_playlist_setting(playlist_name, file_name, folder_settings, folder_path, pretty_print):
    file_path = save_json(file_name, folder_settings, folder_path, 'playlist', pretty_print)
    print("playlist:{0} are saved to {1}".format(playlist_name, file_path))


def get_individual_playlist_setting_and_save(playlists, folder_path, log_file, grafana_url, http_get_headers, verify_ssl, client_cert, debug, pretty_print):
    file_path = folder_path + '/' + log_file
    with open(u"{0}".format(file_path), 'w+') as f:
        for playlist in playlists:
            (status, content) = get_playlist(playlist['id'], grafana_url, http_get_headers, verify_ssl, client_cert, debug)
            if status == 200:
                save_playlist_setting(
                    to_python2_and_3_compatible_string(playlist['name']), 
                    str(playlist['id']),
                    content,
                    folder_path,
                    pretty_print
                )
                f.write('{0}\t{1}\n'.format(playlist['id'], to_python2_and_3_compatible_string(playlist['name'])))
