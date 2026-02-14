import React, { forwardRef, JSX, useImperativeHandle, useState } from "react";
import { Modal } from "react-bootstrap";
import { Accordion } from "../Accordion/Accordion";
import { useConfig } from "../../contexts/ConfigContext";
import { useGlobalToast } from "../../hooks/useNotificationToast";

export interface ScrapingGuideModalHandle {
	show: () => void;
	hide: () => void;
}

export const ScrapingGuideModal = forwardRef<ScrapingGuideModalHandle>((_, ref): JSX.Element => {
	const [visible, setVisible] = useState<boolean>(false);
	const [openSection, setOpenSection] = useState<string | null>(null);
	const { config } = useConfig();
	const { showToastSuccess } = useGlobalToast();

	const toggleSection = (key: string): void => {
		setOpenSection((prev) => (prev === key ? null : key));
	};

	useImperativeHandle(ref, () => ({
		show: (): void => setVisible(true),
		hide: (): void => setVisible(false),
	}));

	const copyEmail = (): void => {
		navigator.clipboard.writeText(config.scraper_email).then((): void => {
			showToastSuccess(`${config.scraper_email} copied to clipboard`);
		});
	};

	return (
		<Modal show={visible} onHide={() => setVisible(false)} centered size="lg">
			<Modal.Header closeButton>
				<Modal.Title>
					<i className="bi bi-envelope-paper me-2" />
					Job Scraping Setup Guide
				</Modal.Title>
			</Modal.Header>
			<Modal.Body>
				<p>
					To enable job scraping, you need to set up an email forwarding rule in your email client. For each
					job platform you use (LinkedIn, Indeed, etc.), create a rule that automatically forwards job alert
					emails to the JAM scraper email address below.
				</p>

				<div className="email-highlight mb-3" onClick={copyEmail} style={{ cursor: "pointer" }}>
					<code>{config?.scraper_email}</code>
					<div className="copy-hint">Click to copy</div>
				</div>

				<p className="mb-3">Select your email client below for step-by-step instructions:</p>

				<Accordion
					header={
						<span>
							<i className="bi bi-google me-2" />
							<strong>Gmail</strong>
						</span>
					}
					isOpen={openSection === "gmail"}
					onToggle={() => toggleSection("gmail")}
				>
					<ol className="mt-2 mb-2">
						<li>
							Open Gmail and click the <strong>gear icon</strong> (top-right), then{" "}
							<strong>See all settings</strong>.
						</li>
						<li>
							Go to the <strong>Forwarding and POP/IMAP</strong> tab.
						</li>
						<li>
							Click <strong>Add a forwarding address</strong> and enter:{" "}
							<code>{config?.scraper_email}</code>
						</li>
						<li>
							Gmail will send a confirmation email to verify the forwarding address. JAM automatically
							detects this and displays a confirmation link on your <strong>Premium settings</strong> page
							(this may take up to 3 hours) - simply click it to confirm.
						</li>
						<li>
							Go back to Settings and click the <strong>Filters and Blocked Addresses</strong> tab.
						</li>
						<li>
							Click <strong>Create a new filter</strong>.
						</li>
						<li>
							In the <strong>From</strong> field, enter the sender address of the job platform (e.g.{" "}
							<code>jobs-noreply@linkedin.com</code>).
						</li>
						<li>
							Click <strong>Create filter</strong>, tick <strong>Forward it to</strong>, select the JAM
							scraper email, and click <strong>Create filter</strong>.
						</li>
					</ol>
				</Accordion>

				<Accordion
					header={
						<span>
							<i className="bi bi-microsoft me-2" />
							<strong>Outlook (Web)</strong>
						</span>
					}
					isOpen={openSection === "outlook-web"}
					onToggle={() => toggleSection("outlook-web")}
				>
					<ol className="mt-2 mb-2">
						<li>
							Open Outlook on the web and click the <strong>gear icon</strong> (top-right) to open
							Settings.
						</li>
						<li>
							Go to <strong>Mail &gt; Rules</strong>.
						</li>
						<li>
							Click <strong>Add new rule</strong>.
						</li>
						<li>Name the rule (e.g. "Forward LinkedIn alerts to JAM").</li>
						<li>
							Under <strong>Add a condition</strong>, choose <strong>From</strong> and enter the job
							platform's sender email.
						</li>
						<li>
							Under <strong>Add an action</strong>, choose <strong>Forward to</strong> and enter:{" "}
							<code>{config?.scraper_email}</code>
						</li>
						<li>
							Click <strong>Save</strong>.
						</li>
					</ol>
				</Accordion>

				<Accordion
					header={
						<span>
							<i className="bi bi-microsoft me-2" />
							<strong>Outlook (Windows)</strong>
						</span>
					}
					isOpen={openSection === "outlook-windows"}
					onToggle={() => toggleSection("outlook-windows")}
				>
					<ol className="mt-2 mb-2">
						<li>
							Open Outlook and go to <strong>File &gt; Manage Rules &amp; Alerts</strong>.
						</li>
						<li>
							Click <strong>New Rule</strong>.
						</li>
						<li>
							Select <strong>Apply rule on messages I receive</strong> and click <strong>Next</strong>.
						</li>
						<li>
							Tick <strong>from people or public group</strong>, then click the underlined link and enter
							the job platform's sender email. Click <strong>Next</strong>.
						</li>
						<li>
							Tick <strong>forward it to people or public group</strong>, then click the underlined link
							and enter: <code>{config?.scraper_email}</code>
						</li>
						<li>
							Click <strong>Next</strong>, review any exceptions, then click <strong>Next</strong> again.
						</li>
						<li>
							Name the rule (e.g. "Forward LinkedIn alerts to JAM"), ensure{" "}
							<strong>Turn on this rule</strong> is ticked, and click <strong>Finish</strong>.
						</li>
					</ol>
				</Accordion>

				<Accordion
					header={
						<span>
							<i className="bi bi-apple me-2" />
							<strong>Apple Mail</strong>
						</span>
					}
					isOpen={openSection === "apple"}
					onToggle={() => toggleSection("apple")}
				>
					<ol className="mt-2 mb-2">
						<li>
							Open Apple Mail and go to <strong>Mail &gt; Preferences</strong> (or{" "}
							<strong>Settings</strong> on macOS Ventura+).
						</li>
						<li>
							Click the <strong>Rules</strong> tab.
						</li>
						<li>
							Click <strong>Add Rule</strong>.
						</li>
						<li>Set a description (e.g. "Forward Indeed alerts to JAM").</li>
						<li>
							Set the condition to <strong>From</strong> contains the job platform's sender email.
						</li>
						<li>
							Set the action to <strong>Forward Message</strong> to: <code>{config?.scraper_email}</code>
						</li>
						<li>
							Click <strong>OK</strong> and apply the rule.
						</li>
					</ol>
				</Accordion>

				<Accordion
					header={
						<span>
							<i className="bi bi-envelope me-2" />
							<strong>Yahoo Mail</strong>
						</span>
					}
					isOpen={openSection === "yahoo"}
					onToggle={() => toggleSection("yahoo")}
				>
					<ol className="mt-2 mb-2">
						<li>
							Open Yahoo Mail and click the <strong>gear icon</strong>, then{" "}
							<strong>More Settings</strong>.
						</li>
						<li>
							Go to <strong>Filters</strong>.
						</li>
						<li>
							Click <strong>Add new filters</strong>.
						</li>
						<li>Name the filter (e.g. "Forward LinkedIn alerts to JAM").</li>
						<li>
							Set <strong>From</strong> to the job platform's sender email.
						</li>
						<li>
							Set the action to <strong>Forward</strong> to: <code>{config?.scraper_email}</code>
						</li>
						<li>
							Click <strong>Save</strong>.
						</li>
					</ol>
				</Accordion>
			</Modal.Body>
		</Modal>
	);
});
