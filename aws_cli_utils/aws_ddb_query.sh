aws dynamodb query \
--table-name pickup-cw-snp \
--key-conditions file://query_item.json \
--region us-west-2 \
--return-consumed-capacity TOTAL