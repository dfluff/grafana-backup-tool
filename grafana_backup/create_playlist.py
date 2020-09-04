import json
from grafana_backup.dashboardApi import create_playlist, search_all_playlists, get_playlist, update_playlist, search_dashboard


def main(args, settings, file_path):
    grafana_url = settings.get('GRAFANA_URL')
    http_post_headers = settings.get('HTTP_POST_HEADERS')
    verify_ssl = settings.get('VERIFY_SSL')
    client_cert = settings.get('CLIENT_CERT')
    debug = settings.get('DEBUG')

    with open(file_path, 'r') as f:
        data = f.read()

    playlist = json.loads(data)
    print(playlist)

    
    # Dashboards within playlists are referenced by id which may not match so we need to match by name and update the id
    # Fixme search more than just the first page of results
    (status, all_dashboards) = search_dashboard(1, 5000, grafana_url, http_post_headers, verify_ssl, client_cert, debug)
    if( status != 200 ):
        return
    
    # We need to clear the list of items and rebuild
    items = playlist['items']
    playlist['items'] = []

    for item in items:
        id = None
        title = item.get('title')
        for dashboard in all_dashboards:
            if (dashboard.get('title') == title):
                print('create_playlist found dashboard {0} as id {1} (backup file said {2})'.format(title, dashboard.get('id'), item['value']))
                id = dashboard.get('id')
                item['value'] = str(id)
                playlist['items'].append(item)
                break

        if( id is None ):
            print('create_playlist failed to find playlist dashboard {0} (backup file said {1})'.format(title, item['value']))


    # Playlists dont have uids so we have to match by name
    (status, msg) = search_all_playlists(grafana_url, http_post_headers, verify_ssl, client_cert, debug)
    print("search_all_playlists {0}, status: {1}, msg: {2}".format(playlist.get('id', ''), status, msg))
    if( status == 200 ):
        id = None
        name = playlist.get('name','')
        for existing_playlist in msg:
            if( existing_playlist.get('name', '') == name ):
                id = existing_playlist.get('id')
                break

        if( id is not None ):
            # Playlist aready exists
            playlist['id'] = id
            print('create playlist  {0} already exists as id {1} - updating'.format(name, id) )
            result = update_playlist(id, json.dumps(playlist), grafana_url, http_post_headers, verify_ssl, client_cert, debug)
            print("update playlist {0}, status: {1}, msg: {2}".format(playlist.get('name', ''), result[0], result[1]))

        else:
            result = create_playlist(json.dumps(playlist), grafana_url, http_post_headers, verify_ssl, client_cert, debug)
            print("create playlist {0}, status: {1}, msg: {2}".format(playlist.get('name', ''), result[0], result[1]))
