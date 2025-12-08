"use client";

import * as React from "react";
import {
  useReactTable,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  ColumnDef,
  flexRender,
  SortingState,
  ColumnFiltersState,
  VisibilityState,
} from "@tanstack/react-table";
import { ArrowUpDown, ChevronRight, ArrowLeftRight, Search, Download, ChevronLeft, ChevronsLeft, ChevronsRight, FileText, MapPin, ExternalLink } from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/select";

interface Application {
  id: string;
  job_id: string;
  candidate_id: string;
  candidate_name: string;
  candidate_email: string;
  candidate_location: string | null;
  resume_url: string | null;
  status: string;
  fit_score: number | null;
  applied_at: string;
}

interface ApplicationsTableProps {
  data: Application[];
  jobId: string;
}

export function ApplicationsTable({ data, jobId }: ApplicationsTableProps) {
  const [sorting, setSorting] = React.useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([]);
  const [columnVisibility, setColumnVisibility] = React.useState<VisibilityState>({});
  const [rowSelection, setRowSelection] = React.useState({});
  const [globalFilter, setGlobalFilter] = React.useState("");
  const [isExporting, setIsExporting] = React.useState(false);

  const columns: ColumnDef<Application>[] = [
    {
      accessorKey: "candidate_name",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            className="h-8 px-2 lg:px-3"
          >
            Candidate
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        );
      },
      cell: ({ row }) => (
        <div className="font-medium">{row.getValue("candidate_name")}</div>
      ),
    },
    {
      accessorKey: "candidate_email",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            className="h-8 px-2 lg:px-3"
          >
            Email
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        );
      },
      cell: ({ row }) => (
        <div className="text-muted-foreground">{row.getValue("candidate_email")}</div>
      ),
    },
    {
      accessorKey: "candidate_location",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            className="h-8 px-2 lg:px-3"
          >
            Location
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        );
      },
      cell: ({ row }) => {
        const location = row.getValue("candidate_location") as string | null;
        return (
          <div className="flex items-center gap-2 text-muted-foreground">
            {location ? (
              <>
                <MapPin className="h-4 w-4" />
                {location}
              </>
            ) : (
              <span>—</span>
            )}
          </div>
        );
      },
    },
    {
      accessorKey: "resume_url",
      header: "CV",
      cell: ({ row }) => {
        const resumeUrl = row.getValue("resume_url") as string | null;
        if (!resumeUrl) {
          return <span className="text-muted-foreground">—</span>;
        }
        return (
          <div className="flex items-center gap-2">
            <a
              href={resumeUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-primary hover:underline"
              onClick={(e) => e.stopPropagation()}
            >
              <FileText className="h-4 w-4" />
              <span className="text-sm">View CV</span>
              <ExternalLink className="h-3 w-3" />
            </a>
          </div>
        );
      },
    },
    {
      accessorKey: "status",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            className="h-8 px-2 lg:px-3"
          >
            Status
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        );
      },
      cell: ({ row }) => {
        const status = row.getValue("status") as string;
        const statusConfig: Record<string, { label: string; variant: "default" | "secondary" | "destructive" | "outline" }> = {
          APPLIED: { label: "Applied", variant: "default" },
          SCREENING: { label: "Screening", variant: "secondary" },
          SHORTLISTED: { label: "Shortlisted", variant: "default" },
          INTERVIEW_SCHEDULED: { label: "Interview Scheduled", variant: "secondary" },
          OFFERED: { label: "Offered", variant: "default" },
          REJECTED: { label: "Rejected", variant: "destructive" },
          HIRED: { label: "Hired", variant: "default" },
        };
        const config = statusConfig[status] || { label: status, variant: "outline" };
        return (
          <Badge variant={config.variant}>
            {config.label}
          </Badge>
        );
      },
      filterFn: (row, id, value) => {
        if (!value || value === "all") return true;
        return row.getValue(id) === value;
      },
    },
    {
      accessorKey: "fit_score",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            className="h-8 px-2 lg:px-3"
          >
            Fit Score
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        );
      },
      cell: ({ row }) => {
        const score = row.getValue("fit_score") as number | null;
        if (score === null) {
          return <span className="text-muted-foreground">—</span>;
        }
        return (
          <div className="flex items-center gap-2">
            <span className="font-medium">{score.toFixed(1)}%</span>
            <div className="w-16 h-2 bg-muted rounded-full overflow-hidden">
              <div
                className={`h-full ${
                  score >= 80 ? "bg-green-500" :
                  score >= 60 ? "bg-yellow-500" :
                  "bg-red-500"
                }`}
                style={{ width: `${score}%` }}
              />
            </div>
          </div>
        );
      },
    },
    {
      accessorKey: "applied_at",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            className="h-8 px-2 lg:px-3"
          >
            Applied Date
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        );
      },
      cell: ({ row }) => {
        const date = new Date(row.getValue("applied_at"));
        return (
          <div className="text-muted-foreground">
            {date.toLocaleDateString("en-US", {
              year: "numeric",
              month: "short",
              day: "numeric",
            })}
          </div>
        );
      },
    },
    {
      id: "actions",
      enableHiding: false,
      cell: ({ row }) => {
        const application = row.original;
        return (
          <Link href={`/recruiter/applications/${application.id}`}>
            <Button variant="ghost" className="h-8 w-8 p-0">
              <span className="sr-only">Open menu</span>
              <ArrowLeftRight className="h-4 w-4" />
            </Button>
          </Link>
        );
      },
    },
  ];

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: setRowSelection,
    onGlobalFilterChange: setGlobalFilter,
    globalFilterFn: "includesString",
    state: {
      sorting,
      columnFilters,
      columnVisibility,
      rowSelection,
      globalFilter,
    },
    initialState: {
      pagination: {
        pageSize: 10,
      },
    },
  });

  const statusFilter = React.useMemo(() => {
    const statuses = Array.from(new Set(data.map((app) => app.status)));
    return statuses;
  }, [data]);

  const handleExport = React.useCallback(async () => {
    setIsExporting(true);
    try {
      const ExcelJS = await import("exceljs");
      
      // Create a new workbook and worksheet
      const workbook = new ExcelJS.Workbook();
      const worksheet = workbook.addWorksheet("Applications");

      // Define columns
      worksheet.columns = [
        { header: "Candidate Name", key: "candidateName", width: 25 },
        { header: "Email", key: "email", width: 30 },
        { header: "Location", key: "location", width: 20 },
        { header: "Status", key: "status", width: 20 },
        { header: "Fit Score", key: "fitScore", width: 12 },
        { header: "Applied Date", key: "appliedDate", width: 18 },
        { header: "CV Link", key: "cvLink", width: 50 },
      ];

      // Style header row
      const headerRow = worksheet.getRow(1);
      headerRow.font = { bold: true, color: { argb: "FFFFFFFF" } };
      headerRow.fill = {
        type: "pattern",
        pattern: "solid",
        fgColor: { argb: "FF3B82F6" },
      };
      headerRow.alignment = { horizontal: "center", vertical: "middle" };
      headerRow.height = 25;

      // Add borders to header
      worksheet.getRow(1).eachCell((cell) => {
        cell.border = {
          top: { style: "thin", color: { argb: "FF1E40AF" } },
          bottom: { style: "thin", color: { argb: "FF1E40AF" } },
          left: { style: "thin", color: { argb: "FF1E40AF" } },
          right: { style: "thin", color: { argb: "FF1E40AF" } },
        };
      });

      // Prepare and add data rows
      const exportData = table.getFilteredRowModel().rows.map((row) => {
        const app = row.original;
        const status = app.status.replace(/_/g, " ");
        return {
          candidateName: app.candidate_name,
          email: app.candidate_email,
          location: app.candidate_location || "N/A",
          status: status,
          fitScore: app.fit_score !== null ? `${app.fit_score.toFixed(1)}%` : "N/A",
          appliedDate: new Date(app.applied_at).toLocaleDateString("en-US", {
            year: "numeric",
            month: "long",
            day: "numeric",
          }),
          cvLink: app.resume_url || "N/A",
        };
      });

      // Add data rows with alternating row colors
      exportData.forEach((row, index) => {
        const worksheetRow = worksheet.addRow(row);
        worksheetRow.alignment = { vertical: "middle" };
        
        // Alternate row colors for better readability
        if (index % 2 === 0) {
          worksheetRow.fill = {
            type: "pattern",
            pattern: "solid",
            fgColor: { argb: "FFF9FAFB" },
          };
        }

        // Add borders to data cells
        worksheetRow.eachCell((cell) => {
          cell.border = {
            top: { style: "thin", color: { argb: "FFE5E7EB" } },
            bottom: { style: "thin", color: { argb: "FFE5E7EB" } },
            left: { style: "thin", color: { argb: "FFE5E7EB" } },
            right: { style: "thin", color: { argb: "FFE5E7EB" } },
          };
        });
      });

      // Freeze header row
      worksheet.views = [{ state: "frozen", ySplit: 1 }];

      // Generate filename with current date
      const dateStr = new Date().toISOString().split("T")[0];
      const filename = `applications_${dateStr}.xlsx`;

      // Write file
      const buffer = await workbook.xlsx.writeBuffer();
      const blob = new Blob([buffer], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setIsExporting(false);
    } catch (error) {
      console.error("Export error:", error);
      setIsExporting(false);
      alert("Failed to export. Please try again.");
    }
  }, [table]);

  return (
    <div className="w-full space-y-4">
      {/* Filters and Search */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex flex-1 items-center gap-2">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search candidates..."
              value={globalFilter ?? ""}
              onChange={(e) => setGlobalFilter(e.target.value)}
              className="pl-9"
            />
          </div>
          <Select
            value={(table.getColumn("status")?.getFilterValue() as string) ?? "all"}
            onChange={(e) => {
              const value = e.target.value;
              table.getColumn("status")?.setFilterValue(
                value === "all" ? undefined : value
              );
            }}
            className="w-[180px]"
          >
            <option value="all">All Statuses</option>
            {statusFilter.map((status) => (
              <option key={status} value={status}>
                {status.replace(/_/g, " ")}
              </option>
            ))}
          </Select>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            size="sm" 
            className="h-9"
            onClick={handleExport}
            disabled={isExporting || data.length === 0}
          >
            <Download className="mr-2 h-4 w-4" />
            {isExporting ? "Exporting..." : "Export to Excel"}
          </Button>
        </div>
      </div>

      {/* Table */}
      <div className="rounded-md border bg-card">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id}>
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                    </TableHead>
                  );
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                  className="cursor-pointer hover:bg-muted/50"
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between px-2">
        <div className="flex-1 text-sm text-muted-foreground">
          Showing {table.getRowModel().rows.length} of{" "}
          {table.getFilteredRowModel().rows.length} application(s).
        </div>
        <div className="flex items-center space-x-6 lg:space-x-8">
          <div className="flex items-center space-x-2">
            <p className="text-sm font-medium">Rows per page</p>
            <Select
              value={`${table.getState().pagination.pageSize}`}
              onChange={(e) => {
                table.setPageSize(Number(e.target.value));
              }}
              className="h-8 w-[70px]"
            >
              <option value="10">10</option>
              <option value="20">20</option>
              <option value="30">30</option>
              <option value="50">50</option>
            </Select>
          </div>
          <div className="flex w-[100px] items-center justify-center text-sm font-medium">
            Page {table.getState().pagination.pageIndex + 1} of{" "}
            {table.getPageCount()}
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              className="hidden h-8 w-8 p-0 lg:flex"
              onClick={() => table.setPageIndex(0)}
              disabled={!table.getCanPreviousPage()}
            >
              <span className="sr-only">Go to first page</span>
              <ChevronsLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              className="h-8 w-8 p-0"
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
            >
              <span className="sr-only">Go to previous page</span>
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              className="h-8 w-8 p-0"
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
            >
              <span className="sr-only">Go to next page</span>
              <ChevronRight className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              className="hidden h-8 w-8 p-0 lg:flex"
              onClick={() => table.setPageIndex(table.getPageCount() - 1)}
              disabled={!table.getCanNextPage()}
            >
              <span className="sr-only">Go to last page</span>
              <ChevronsRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

