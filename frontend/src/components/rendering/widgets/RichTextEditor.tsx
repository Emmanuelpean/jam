import React, { JSX, useEffect } from "react";
import { EditorContent, useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Placeholder from "@tiptap/extension-placeholder";
import { WidgetProps } from "./WidgetRenders";
import { toKey } from "../../../utils/StringUtils";
import "./RichTextEditor.scss";

interface ToolbarButtonProps {
	icon: string;
	label: string;
	isActive?: boolean;
	isDisabled?: boolean;
	onClick: () => void;
}

const ToolbarButton = ({ icon, label, isActive, isDisabled, onClick }: ToolbarButtonProps): JSX.Element => (
	<button
		type="button"
		className={`rich-text-toolbar-btn${isActive ? " active" : ""}`}
		aria-label={label}
		title={label}
		disabled={isDisabled}
		onMouseDown={(e: React.MouseEvent): void => e.preventDefault()}
		onClick={onClick}
	>
		<i className={`bi ${icon}`} />
	</button>
);

export const RichTextEditor = ({ field, value, handleChange, error }: WidgetProps): JSX.Element => {
	const charCount: number = field.maxChars ? (value || "").length : 0;
	const isOverLimit: boolean = field.maxChars ? charCount > field.maxChars : false;

	const editor = useEditor({
		extensions: [
			StarterKit.configure({ link: { openOnClick: false, autolink: true } }),
			Placeholder.configure({ placeholder: field.placeholder || "" }),
		],
		content: value || "",
		editable: !field.isDisabled,
		onUpdate: ({ editor }): void => {
			handleChange({ target: { name: toKey(field.key), value: editor.isEmpty ? "" : editor.getHTML() } });
		},
	});

	// Keep the editor in sync when the field value changes externally (e.g. form reset, editing a different record).
	useEffect((): void => {
		if (editor && !editor.isFocused && (value || "") !== editor.getHTML()) {
			editor.commands.setContent(value || "", { emitUpdate: false });
		}
	}, [value, editor]);

	useEffect((): void => {
		editor?.setEditable(!field.isDisabled);
	}, [field.isDisabled, editor]);

	if (!editor) return <></>;

	const setLink = (): void => {
		const previousUrl: string | undefined = editor.getAttributes("link").href as string | undefined;
		const url: string | null = window.prompt("Enter a URL", previousUrl || "https://");
		if (url === null) return;
		if (url === "") {
			editor.chain().focus().extendMarkRange("link").unsetLink().run();
			return;
		}
		editor.chain().focus().extendMarkRange("link").setLink({ href: url }).run();
	};

	return (
		<div
			className={`rich-text-editor${isOverLimit || error ? " is-invalid" : ""}${
				field.isDisabled ? " is-disabled" : ""
			}`}
		>
			<div className="rich-text-toolbar">
				<ToolbarButton
					icon="bi-type-bold"
					label="Bold"
					isActive={editor.isActive("bold")}
					onClick={() => editor.chain().focus().toggleBold().run()}
				/>
				<ToolbarButton
					icon="bi-type-italic"
					label="Italic"
					isActive={editor.isActive("italic")}
					onClick={() => editor.chain().focus().toggleItalic().run()}
				/>
				<ToolbarButton
					icon="bi-type-underline"
					label="Underline"
					isActive={editor.isActive("underline")}
					onClick={() => editor.chain().focus().toggleUnderline().run()}
				/>
				<ToolbarButton
					icon="bi-type-strikethrough"
					label="Strikethrough"
					isActive={editor.isActive("strike")}
					onClick={() => editor.chain().focus().toggleStrike().run()}
				/>
				<span className="rich-text-toolbar-divider" />
				<ToolbarButton
					icon="bi-type-h2"
					label="Heading"
					isActive={editor.isActive("heading", { level: 2 })}
					onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
				/>
				<ToolbarButton
					icon="bi-type-h3"
					label="Subheading"
					isActive={editor.isActive("heading", { level: 3 })}
					onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
				/>
				<span className="rich-text-toolbar-divider" />
				<ToolbarButton
					icon="bi-list-ul"
					label="Bullet list"
					isActive={editor.isActive("bulletList")}
					onClick={() => editor.chain().focus().toggleBulletList().run()}
				/>
				<ToolbarButton
					icon="bi-list-ol"
					label="Numbered list"
					isActive={editor.isActive("orderedList")}
					onClick={() => editor.chain().focus().toggleOrderedList().run()}
				/>
				<ToolbarButton
					icon="bi-blockquote-left"
					label="Quote"
					isActive={editor.isActive("blockquote")}
					onClick={() => editor.chain().focus().toggleBlockquote().run()}
				/>
				<span className="rich-text-toolbar-divider" />
				<ToolbarButton icon="bi-link-45deg" label="Link" isActive={editor.isActive("link")} onClick={setLink} />
				<ToolbarButton
					icon="bi-eraser"
					label="Clear formatting"
					onClick={() => editor.chain().focus().clearNodes().unsetAllMarks().run()}
				/>
				<span className="rich-text-toolbar-spacer" />
				<ToolbarButton
					icon="bi-arrow-counterclockwise"
					label="Undo"
					isDisabled={!editor.can().undo()}
					onClick={() => editor.chain().focus().undo().run()}
				/>
				<ToolbarButton
					icon="bi-arrow-clockwise"
					label="Redo"
					isDisabled={!editor.can().redo()}
					onClick={() => editor.chain().focus().redo().run()}
				/>
			</div>
			<EditorContent editor={editor} className="rich-text-content" id={toKey(field.key)} />
		</div>
	);
};
