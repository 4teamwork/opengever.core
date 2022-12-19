from logging import getLogger
from opengever.base.addressblock.interfaces import IAddressBlockData
from zope.component import queryAdapter


logger = getLogger(__name__)


def get_addressblock_docprops(context, prefix=None):
    try:
        properties = {}
        address_block = queryAdapter(context, IAddressBlockData)

        if address_block:
            key = '.'.join(filter(None, ['ogg', prefix, 'address.block']))
            properties.update({key: address_block.format()})

        return properties

    except Exception as exc:
        logger.warn('Failed to render address block for %r' % context)
        logger.exception(exc)
        return {}
