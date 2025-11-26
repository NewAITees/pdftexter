"""
PDF変換モジュール
"""

import os
import threading
from pathlib import Path
from typing import Optional

import tkinter as tk
from PIL import Image
from reportlab.pdfgen import canvas

from pdftexter.utils.file import get_image_files, join_path
from pdftexter.utils.gui import select_folder, show_error, show_info


class PDFConverter:
    """画像からPDFへの変換クラス"""
    
    def __init__(self):
        """初期化"""
        pass
    
    def convert_images_to_pdf(
        self,
        folder_path: str,
        output_folder: str,
        output_filename: str,
        progress_var: Optional[tk.DoubleVar] = None,
        status_var: Optional[tk.StringVar] = None,
        root: Optional[tk.Tk] = None,
    ) -> bool:
        """
        指定フォルダ内の画像をPDFに変換する
        
        Args:
            folder_path: 画像ファイルがあるフォルダパス
            output_folder: PDF出力先フォルダパス
            output_filename: 出力PDFファイル名
            progress_var: 進捗表示用の変数（GUI使用時）
            status_var: ステータス表示用の変数（GUI使用時）
            root: Tkinterルートウィンドウ（GUI使用時）
            
        Returns:
            変換成功の場合True
        """
        # 画像ファイルの取得とソート
        image_files = get_image_files(folder_path)
        
        if not image_files:
            if root:
                show_error("エラー", "指定されたフォルダに画像ファイルが見つかりません。")
            return False
        
        # PDFファイルパスの生成（拡張子が既にある場合は追加しない）
        if not output_filename.lower().endswith('.pdf'):
            output_filename += '.pdf'
        
        output_pdf = join_path(output_folder, output_filename)
        
        # PDFの作成
        try:
            pdf_canvas = canvas.Canvas(output_pdf)
        except Exception as e:
            if root:
                show_error("エラー", f"PDFファイルの初期化に失敗しました: {e}")
            return False
        
        total_files = len(image_files)
        
        try:
            for i, image_file in enumerate(image_files, 1):
                # 画像の読み込みとPDFページの作成
                full_path = join_path(folder_path, image_file)
                try:
                    img = Image.open(full_path)
                    width, height = img.size
                    pdf_canvas.setPageSize((width, height))
                    pdf_canvas.drawImage(full_path, 0, 0, width, height)
                    pdf_canvas.showPage()
                except Exception as e:
                    error_msg = f"画像ファイル '{image_file}' の処理に失敗しました: {e}"
                    if root:
                        show_error("エラー", error_msg)
                    print(error_msg)
                    continue
                
                # 進捗状況の更新
                if progress_var is not None and status_var is not None and root is not None:
                    progress = (i / total_files) * 100
                    progress_var.set(progress)
                    status_var.set(f"処理中... {i}/{total_files} ファイル")
                    root.update_idletasks()
            
            # PDFを保存
            pdf_canvas.save()
            
            if progress_var is not None and status_var is not None and root is not None:
                progress_var.set(100)
                status_var.set("完了")
            
            return True
            
        except Exception as e:
            error_msg = f"PDF変換中にエラーが発生しました: {e}"
            if root:
                show_error("エラー", error_msg)
            print(error_msg)
            return False


class PDFConverterGUI:
    """PDF変換GUIクラス"""
    
    def __init__(self):
        """初期化"""
        self.root: Optional[tk.Tk] = None
        self.converter = PDFConverter()
    
    def setup_gui(self) -> None:
        """GUIの設定"""
        self.root = tk.Tk()
        self.root.title("Image to PDF Converter")
        
        # 変数の初期化
        folder_var = tk.StringVar()
        output_folder_var = tk.StringVar()
        output_filename_var = tk.StringVar()
        progress_var = tk.DoubleVar()
        status_var = tk.StringVar()
        
        # フォルダ選択部分のUI
        tk.Label(self.root, text="画像があるフォルダを選択:").grid(
            row=0, column=0, sticky="e", padx=5, pady=5
        )
        tk.Entry(self.root, textvariable=folder_var, width=50).grid(
            row=0, column=1, padx=5, pady=5
        )
        tk.Button(
            self.root,
            text="参照",
            command=lambda: folder_var.set(select_folder() or folder_var.get()),
        ).grid(row=0, column=2, padx=5, pady=5)
        
        tk.Label(self.root, text="PDFファイルの出力先フォルダを選択:").grid(
            row=1, column=0, sticky="e", padx=5, pady=5
        )
        tk.Entry(self.root, textvariable=output_folder_var, width=50).grid(
            row=1, column=1, padx=5, pady=5
        )
        tk.Button(
            self.root,
            text="参照",
            command=lambda: output_folder_var.set(
                select_folder() or output_folder_var.get()
            ),
        ).grid(row=1, column=2, padx=5, pady=5)
        
        # ファイル名入力部分のUI
        tk.Label(self.root, text="出力ファイル名:").grid(
            row=2, column=0, sticky="e", padx=5, pady=5
        )
        tk.Entry(self.root, textvariable=output_filename_var, width=50).grid(
            row=2, column=1, padx=5, pady=5
        )
        
        # 変換ボタン
        convert_button = tk.Button(
            self.root,
            text="変換",
            command=lambda: self._run_conversion(
                folder_var,
                output_folder_var,
                output_filename_var,
                progress_var,
                status_var,
                convert_button,
            ),
        )
        convert_button.grid(row=3, column=0, columnspan=3, pady=10)
        
        # プログレスバーとステータス表示
        from tkinter import ttk
        
        progress_bar = ttk.Progressbar(self.root, variable=progress_var, maximum=100)
        progress_bar.grid(row=4, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        status_label = tk.Label(self.root, textvariable=status_var)
        status_label.grid(row=5, column=0, columnspan=3, pady=5)
    
    def _run_conversion(
        self,
        folder_var: tk.StringVar,
        output_folder_var: tk.StringVar,
        output_filename_var: tk.StringVar,
        progress_var: tk.DoubleVar,
        status_var: tk.StringVar,
        convert_button: tk.Button,
    ) -> None:
        """
        変換処理を実行する
        
        Args:
            folder_var: 入力フォルダパスの変数
            output_folder_var: 出力フォルダパスの変数
            output_filename_var: 出力ファイル名の変数
            progress_var: 進捗表示用の変数
            status_var: ステータス表示用の変数
            convert_button: 変換ボタン
        """
        # 入力値の取得と検証
        folder_path = folder_var.get()
        output_folder = output_folder_var.get()
        output_filename = output_filename_var.get()
        
        if not folder_path or not output_folder or not output_filename:
            show_error(
                "エラー",
                "入力フォルダ、出力フォルダ、ファイル名をすべて指定してください。",
            )
            return
        
        # UI状態の初期化
        progress_var.set(0)
        status_var.set("開始中...")
        convert_button.config(state=tk.DISABLED)
        
        def conversion_thread() -> None:
            """変換処理を実行するスレッド"""
            success = self.converter.convert_images_to_pdf(
                folder_path,
                output_folder,
                output_filename,
                progress_var,
                status_var,
                self.root,
            )
            
            # 変換完了後のUI操作はメインスレッドで実行
            if self.root:
                self.root.after(
                    0,
                    lambda: self._post_conversion(
                        success, output_folder, output_filename, convert_button
                    ),
                )
        
        # 別スレッドで変換処理を実行
        thread = threading.Thread(target=conversion_thread)
        thread.start()
    
    def _post_conversion(
        self,
        success: bool,
        output_folder: str,
        output_filename: str,
        convert_button: tk.Button,
    ) -> None:
        """変換完了後の処理"""
        if success:
            output_path = join_path(output_folder, output_filename)
            show_info("完了", f"PDFファイルが作成されました: {output_path}")
            if self.root:
                convert_button.config(text="終了", command=self.root.quit)
        convert_button.config(state=tk.NORMAL)
    
    def run(self) -> None:
        """GUIを実行"""
        if self.root:
            self.root.mainloop()


def main() -> None:
    """メイン関数"""
    gui = PDFConverterGUI()
    gui.setup_gui()
    gui.run()


if __name__ == "__main__":
    main()

