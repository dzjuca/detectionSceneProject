import functions_file

video_path = 'MadMax.mp4'
# scenes = functions_file.find_scenes5(video_path)
scenes = functions_file.find_scenes5(video_path, threshold=3.0, min_content_val=6.0, min_scene_length=2.0)

# Imprimir los tiempos de inicio y fin de cada escena
# for start_time, end_time in scenes:
#     print(f"Inicio: {start_time}, Fin: {end_time}")

if scenes is not None:
    for i, (start_time, end_time) in enumerate(scenes):
        print(f"Escena {i+1}: Desde {start_time.get_timecode()} hasta {end_time.get_timecode()}")
else:
    print("No se pudieron detectar escenas.")

functions_file.split_video3(video_path, scenes, output_dir="output1", use_copy=True, quiet=True)
# functions_file.split_video3(video_path, scenes, output_dir="output2", high_quality=True, quiet=True)
# functions_file.split_video3(video_path, scenes, output_dir="output3", use_mkvmerge=True, quiet=True)
# functions_file.split_video3(video_path, scenes, output_dir="output4", rate_factor=20, preset="medium", quiet=True)

