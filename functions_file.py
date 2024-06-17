import os
import cv2
import subprocess
from moviepy.editor import VideoFileClip, concatenate_videoclips
from scenedetect.detectors import ContentDetector
from scenedetect import VideoManager
from scenedetect import open_video, SceneManager
from scenedetect.detectors import AdaptiveDetector

def detectar_cambios_escena(video_path):
    cap = cv2.VideoCapture(video_path)
    escena_actual = None
    cambios = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if escena_actual is None:
            escena_actual = frame
        else:
            diferencia = cv2.absdiff(escena_actual, frame)
            gris = cv2.cvtColor(diferencia, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gris, (5, 5), 0)
            _, umbral = cv2.threshold(blur, 25, 255, cv2.THRESH_BINARY)
            contornos, _ = cv2.findContours(umbral, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(contornos) > 50:
                cambios.append(cap.get(cv2.CAP_PROP_POS_MSEC))
                escena_actual = frame

    cap.release()
    return cambios
def aplicar_jump_cut(video_path, cambios_escena):
    clips = []
    inicio = 0
    for cambio in cambios_escena:
        clip = VideoFileClip(video_path).subclip(inicio / 1000, cambio / 1000)
        clips.append(clip)
        inicio = cambio

    video_final = concatenate_videoclips(clips)
    video_final.write_videofile("resumen_jump_cut.mp4", codec="libx264")

def find_scenes1(video_path):
    # Crear una instancia de VideoManager y SceneManager
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()

    # Añadir un detector de escenas
    scene_manager.add_detector(ContentDetector())

    # Iniciar el VideoManager
    video_manager.start()

    # Detectar escenas en el video
    scene_manager.detect_scenes(frame_source=video_manager)

    # Obtener y retornar las escenas detectadas
    return scene_manager.get_scene_list()

def find_scenes2(video_path):
    """
    Detecta cambios de escena en un video y retorna una lista de escenas detectadas.

    Parameters:
    video_path (str): La ruta del archivo de video.

    Returns:
    list: Una lista de tuplas con el inicio y el final de cada escena detectada.
    """
    try:
        # Crear una instancia de VideoManager y SceneManager
        video_manager = VideoManager([video_path])
        scene_manager = SceneManager()

        # Añadir un detector de escenas
        scene_manager.add_detector(ContentDetector())

        # Iniciar el VideoManager
        video_manager.start()

        # Detectar escenas en el video
        scene_manager.detect_scenes(frame_source=video_manager)

        # Obtener y retornar las escenas detectadas
        scene_list = scene_manager.get_scene_list()

        return scene_list

    except Exception as e:
        print(f"Ocurrió un error al procesar el video: {e}")
        return None

    finally:
        # Asegurarse de liberar recursos
        video_manager.release()

def find_scenes3(video_path, min_scene_length=2.0):
    """
    Detecta cambios de escena en un video y retorna una lista de escenas detectadas,
    fusionando escenas que duren menos de un tiempo mínimo especificado con las adyacentes.

    Parameters:
    video_path (str): La ruta del archivo de video.
    min_scene_length (float): La duración mínima de una escena en segundos.

    Returns:
    list: Una lista de tuplas con el inicio y el final de cada escena detectada.
    """
    try:
        # Crear una instancia de VideoManager y SceneManager
        video_manager = VideoManager([video_path])
        scene_manager = SceneManager()

        # Añadir un detector de escenas
        scene_manager.add_detector(ContentDetector())

        # Iniciar el VideoManager
        video_manager.start()

        # Detectar escenas en el video
        scene_manager.detect_scenes(frame_source=video_manager)

        # Obtener y retornar las escenas detectadas
        scene_list = scene_manager.get_scene_list()

        # Filtrar y fusionar escenas demasiado cortas
        filtered_scenes = []
        for i in range(len(scene_list)):
            start_time = scene_list[i][0].get_seconds()
            end_time = scene_list[i][1].get_seconds()
            duration = end_time - start_time

            if duration < min_scene_length:
                if filtered_scenes:
                    # Fusionar con la escena anterior
                    filtered_scenes[-1] = (filtered_scenes[-1][0], scene_list[i][1])
                elif i < len(scene_list) - 1:
                    # Fusionar con la siguiente escena si es la primera y hay más escenas
                    filtered_scenes.append((scene_list[i][0], scene_list[i+1][1]))
            else:
                filtered_scenes.append(scene_list[i])

        return filtered_scenes

    except Exception as e:
        print(f"Ocurrió un error al procesar el video: {e}")
        return None

    finally:
        # Asegurarse de liberar recursos
        video_manager.release()

def find_scenes4(video_path, min_scene_length=2.0):
    """
    Detecta cambios de escena en un video y retorna una lista de escenas detectadas,
    fusionando escenas que duren menos de un tiempo mínimo especificado con las adyacentes.

    Parameters:
    video_path (str): La ruta del archivo de video.
    min_scene_length (float): La duración mínima de una escena en segundos.

    Returns:
    list: Una lista de tuplas con el inicio y el final de cada escena detectada.
    """
    try:
        # Crear una instancia de VideoManager y SceneManager
        video_manager = VideoManager([video_path])
        scene_manager = SceneManager()

        # Añadir un detector de escenas
        scene_manager.add_detector(ContentDetector())

        # Iniciar el VideoManager
        video_manager.start()

        # Detectar escenas en el video
        scene_manager.detect_scenes(frame_source=video_manager)

        # Obtener la lista de escenas detectadas
        scene_list = scene_manager.get_scene_list()

        # Filtrar y fusionar escenas demasiado cortas
        filtered_scenes = []
        current_scene = scene_list[0]

        for next_scene in scene_list[1:]:
            start_time, end_time = current_scene
            next_start_time, next_end_time = next_scene
            duration = end_time.get_seconds() - start_time.get_seconds()

            if duration < min_scene_length:
                # Fusionar la escena actual con la siguiente
                current_scene = (start_time, next_end_time)
            else:
                filtered_scenes.append(current_scene)
                current_scene = next_scene

        # Añadir la última escena procesada
        filtered_scenes.append(current_scene)

        return filtered_scenes

    except Exception as e:
        print(f"Ocurrió un error al procesar el video: {e}")
        return None

    finally:
        # Asegurarse de liberar recursos
        video_manager.release()

def split_video1(video_path, scenes, output_folder="output"):
    for i, (start_time, end_time) in enumerate(scenes):
        # Formateamos el nombre del archivo de salida para cada fragmento
        output_filename = f"{output_folder}/scene_{i + 1}.mp4"

        # Creamos el comando para ffmpeg
        # Usamos el formato hh:mm:ss para los tiempos de inicio y fin
        start_time_str = f"{start_time.hours:02d}:{start_time.minutes:02d}:{start_time.seconds:02d}.{int(start_time.get_frames() / start_time.framerate * 1000)}"
        end_time_str = f"{end_time.hours:02d}:{end_time.minutes:02d}:{end_time.seconds:02d}.{int(end_time.get_frames() / end_time.framerate * 1000)}"
        command = [
            "ffmpeg", "-y",  # -y para sobreescribir archivos sin preguntar
            "-i", video_path,  # Archivo de entrada
            "-ss", start_time_str,  # Tiempo de inicio
            "-to", end_time_str,  # Tiempo de fin
            "-c", "copy",  # Copiar los streams sin re-codificar
            output_filename  # Archivo de salida
        ]

        # Ejecutamos el comando
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def split_video2(video_path, scenes, output_folder="output"):

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for i, (start_time, end_time) in enumerate(scenes):
        # Formateamos el nombre del archivo de salida para cada fragmento
        output_filename = f"{output_folder}/scene_{i + 1}.mp4"

        # Obtenemos el tiempo de inicio y fin como string directamente del FrameTimecode
        start_time_str = start_time.get_timecode()
        end_time_str = end_time.get_timecode()

        # Creamos el comando para ffmpeg
        command = [
            "ffmpeg", "-y",  # -y para sobreescribir archivos sin preguntar
            "-i", video_path,  # Archivo de entrada
            "-ss", start_time_str,  # Tiempo de inicio
            "-to", end_time_str,  # Tiempo de fin
            "-c", "copy",  # Copiar los streams sin re-codificar
            output_filename  # Archivo de salida
        ]

        # Ejecutamos el comando
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
def find_scenes5(video_path, threshold=3.0, min_content_val=15.0, min_scene_length=2.0):
    """
    Detecta cambios de escena en un video utilizando el detector adaptativo y retorna una lista de escenas detectadas,
    fusionando escenas que duren menos de un tiempo mínimo especificado con las adyacentes.

    Parameters:
    video_path (str): La ruta del archivo de video.
    threshold (float): El umbral que debe exceder el puntaje del cuadro para desencadenar un corte.
    min_content_val (float): El valor mínimo de contenido que debe exceder para desencadenar un corte.
    min_scene_length (float): La duración mínima de una escena en segundos.

    Returns:
    list: Una lista de tuplas con el inicio y el final de cada escena detectada.
    """
    try:
        # Abrir el video usando open_video
        video = open_video(video_path)
        scene_manager = SceneManager()

        # Añadir un detector adaptativo de escenas
        scene_manager.add_detector(AdaptiveDetector(
            adaptive_threshold=threshold,
            min_content_val=min_content_val
        ))

        # Detectar escenas en el video
        scene_manager.detect_scenes(video)

        # Obtener la lista de escenas detectadas
        scene_list = scene_manager.get_scene_list()

        # Filtrar y fusionar escenas demasiado cortas
        filtered_scenes = []
        current_scene = scene_list[0]

        for next_scene in scene_list[1:]:
            start_time, end_time = current_scene
            next_start_time, next_end_time = next_scene
            duration = end_time.get_seconds() - start_time.get_seconds()

            if duration < min_scene_length:
                # Fusionar la escena actual con la siguiente
                current_scene = (start_time, next_end_time)
            else:
                filtered_scenes.append(current_scene)
                current_scene = next_scene

        # Añadir la última escena procesada
        filtered_scenes.append(current_scene)

        return filtered_scenes

    except Exception as e:
        print(f"Ocurrió un error al procesar el video: {e}")
        return None

def split_video3(video_path, scenes, output_dir="output", filename_format="$VIDEO_NAME-Scene-$SCENE_NUMBER", use_copy=False, high_quality=False, rate_factor=22, preset="veryfast", use_mkvmerge=False, quiet=False):
    """
    Divide un video en escenas detectadas utilizando scenedetect.

    Parameters:
    video_path (str): La ruta del archivo de video.
    scenes (list): Lista de escenas detectadas.
    output_dir (str): Directorio de salida para guardar los videos. Default es "output".
    filename_format (str): Formato del nombre del archivo para los videos. Default es "$VIDEO_NAME-Scene-$SCENE_NUMBER".
    use_copy (bool): Si se debe copiar el video sin re-codificar. Default es False.
    high_quality (bool): Si se debe usar alta calidad en la re-codificación. Default es False.
    rate_factor (int): El factor de tasa constante (CRF) para la codificación. Default es 22.
    preset (str): El preset de compresión para la codificación. Default es "veryfast".
    use_mkvmerge (bool): Si se debe usar mkvmerge en lugar de ffmpeg. Default es False.
    quiet (bool): Si se debe ocultar la salida de la herramienta externa de división de video. Default es False.
    """
    try:
        # Comando base para scenedetect
        command = ["scenedetect", "-i", video_path, "split-video", "-o", output_dir, "-f", filename_format]

        # Añadir opciones basadas en los parámetros
        if use_copy:
            command.append("--copy")
        elif high_quality:
            command.append("--high-quality")
        elif use_mkvmerge:
            command.append("--mkvmerge")
        else:
            command.extend(["--rate-factor", str(rate_factor), "--preset", preset])

        if quiet:
            command.append("--quiet")

        # Ejecutar el comando
        subprocess.run(command, check=True)
        print("Video dividido exitosamente en escenas.")

    except subprocess.CalledProcessError as e:
        print(f"Error al dividir el video en escenas: {e}")










