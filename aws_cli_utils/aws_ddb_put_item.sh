aws dynamodb put-item \
--table-name pickup-cw-snp \
--item file://put_item.json \
--region "us-west-2" \
--return-consumed-capacity TOTAL  
