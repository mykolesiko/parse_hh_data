#from parse_hh_data 
import download, parse
import json

#ids = download.resume_ids(
#    area_id=113, #Russia https://github.com/hhru/api/blob/master/docs/areas.md
##    specialization_id=1, #"Информационные технологии, интернет, телеком" https://api.hh.ru/specializations
 #   search_period=1, 
 #   num_pages=100,
 #   )
data = []
resume = download.resume('fca5698aff08aa635d0039ed1f447631434632')#('c14ed28400078189690039ed1f4a566f4b7739')
#print(resume)
data.append(parse.resume(resume))


with open('resume.json', 'w', encoding ='utf8') as outfile:
    json.dump(data, outfile, indent=4, ensure_ascii=False)



