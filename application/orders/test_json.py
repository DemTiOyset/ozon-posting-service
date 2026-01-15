a = {
  "notificationType": "ORDER_CREATED",
  "campaignId": 100200300,
  "orderId": 52701397891,
  "createdAt": "2025-12-29T10:15:30.213Z",
  "items": [
    {"offerId": "SKU-IPHONE-15-128-BLK", "count": 1},
    {"offerId": "SKU-CASE-SILICONE-RED", "count": 2}
  ]
}

b = {
  "notificationType": "ORDER_CREATED",
  "campaignId": 100200300,
  "orderId": 52701397891,
  "createdAt": "2025-12-29T11:02:10.000Z",
  "items": [
    {"offerId": "SKU-PS5-DUALSENSE-WHT", "count": 1}
  ]
}

c = {
  "notificationType": "ORDER_CREATED",
  "campaignId": 100200301,
  "orderId": 52701397891,
  "createdAt": "2025-12-29T12:44:59.759Z",
  "items": [
    {"offerId": "SKU-SSD-NVME-1TB", "count": 1},
    {"offerId": "SKU-THERMAL-PASTE-4G", "count": 1}
  ]
}

d = {
  "notificationType": "ORDER_CREATED",
  "campaignId": 100200302,
  "orderId": 52701397891,
  "createdAt": "2025-12-29T18:20:05.100Z",
  "items": [
    {"offerId": "SKU-TEA-GREEN-100", "count": 3}
  ]
}


e = {
  "notificationType": "ORDER_CREATED",
  "campaignId": 100200302,
  "orderId": 52701397891,
  "createdAt": "2025-12-29T21:59:59.999Z",
  "items": [
    {"offerId": "SKU-BOOK-ARCH-PY", "count": 1},
    {"offerId": "SKU-NOTEBOOK-A5", "count": 5}
  ]
}


update = {
  "notificationType": "ORDER_STATUS_UPDATED",
  "campaignId": 100200300,
  "orderId": 52701397891,
  "status": "PROCESSING",
  "substatus": "STARTED",
  "updatedAt": "2025-12-30T10:15:30.123Z"
}

updated = {
  "notificationType": "ORDER_UPDATED",
  "campaignId": 100200300,
  "orderId": 52701397891,
  "updateType": "SHIPMENT_DATE_UPDATED",
  "updatedAt": "2025-12-30T10:15:30.123Z"
}

