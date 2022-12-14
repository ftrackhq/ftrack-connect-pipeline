# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack
import os
import appdirs
import tempfile
import six

from ftrack_connect_pipeline import constants as core_constants


def str_context(context, with_id=False, force_version_nr=None, delimiter='/'):
    '''Utility function to produce a human readable string out or a context.'''
    if not 'project' in context:
        return str(context)
    return '{}/{}'.format(
        context['project']['name'],
        '/'.join(['{}'.format(link['name']) for link in context['link'][1:]]),
    ).replace('/', delimiter)


def str_version(v, with_id=False, force_version_nr=None, delimiter='/'):
    '''Utility function to produce a human readable string out or an asset version.'''
    return '{}/{}/v{}{}'.format(
        str_context(v['task']),
        v['asset']['name'],
        force_version_nr or v['version'],
        ('({})'.format(v['id']) if with_id else ''),
    ).replace('/', delimiter)


def safe_string(string):
    if six.PY2 and isinstance(string, unicode):
        return string.encode('utf-8')
    if isinstance(string, bytes):
        return string.decode("utf-8")
    return str(string)


def get_save_path(context_id, session, extension=None, temp=True):
    '''Calculate the path to local save (work path), DCC independent'''

    result = False
    message = None

    if temp:
        result = os.path.join(
            tempfile.gettempdir(),
            'ftrack-connect',
            'ftrack',
            '{}{}'.format(
                os.path.basename(tempfile.NamedTemporaryFile().name),
                extension if extension else '',
            ),
        )
        if not os.path.exists(os.path.dirname(result)):
            os.makedirs(os.path.dirname(result))
    else:
        if context_id is None:
            raise Exception(
                'Could not get save path- no context id provided'.format(
                    context_id
                )
            )

        context = session.query(
            'Context where id={}'.format(context_id)
        ).first()

        if context is None:
            raise Exception(
                'Could not get save path - unknown context: {}'.format(
                    context_id
                )
            )

        server_folder_name = (
            session.server_url.split('//')[-1].split('.')[0].replace('-', '_')
        )
        save_path_base = os.environ.get('FTRACK_SAVE_PATH')
        if save_path_base is None:
            save_path_base = os.path.join(
                appdirs.user_data_dir('ftrack-connect', 'ftrack'),
                core_constants.SNAPSHOT_COMPONENT_NAME,
                server_folder_name,
            )

        # Try to query location system (future) for getting task path
        try:
            location = session.pick_location()
            save_path = os.path.join(
                save_path_base, location.get_filesystem_path(context)
            )
        except:
            structure_names = [
                context['project']['name'].replace(' ', '_').lower()
            ] + [
                item['name'].replace(' ', '_').lower()
                for item in context['link'][1:]
            ]

            # Build path down to context
            save_path = os.sep.join([save_path_base] + structure_names)

        if save_path is not None:
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            if not os.path.exists(save_path):
                return (
                    None,
                    'Could not create save directory: {}!'.format(save_path),
                )

            # Find latest version number
            next_version_number = 1
            latest_asset_version = session.query(
                'AssetVersion where '
                'task.id={} and is_latest_version=true'.format(context_id)
            ).first()
            if latest_asset_version:
                next_version_number = latest_asset_version['version'] + 1

            # TODO: use task type <> asset type mappings
            filename = context['type'][
                'name'
            ].lower()  # modeling, compositing...

            # Make sure we do not overwrite existing work done
            save_path = os.path.join(
                save_path, '%s_v%03d' % (filename, next_version_number)
            )

            while os.path.exists(save_path) or (
                extension
                and os.path.exists('{}{}'.format(save_path, extension))
            ):
                next_version_number += 1
                save_path = os.path.join(
                    os.path.dirname(save_path),
                    '%s_v%03d' % (filename, next_version_number),
                )

            result = save_path
        else:
            message = 'Could not evaluate local save path!'

    return result, message
